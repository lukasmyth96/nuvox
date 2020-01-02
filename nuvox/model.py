import os
from datetime import datetime
import pickle
import random


import numpy as np

from keras.layers import Input, LSTM, TimeDistributed, Dense
from keras.models import Sequential, load_model
from keras.utils import to_categorical
from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping

from nuvox.traces import get_random_trace
from nuvox.utils.common import pickle_save, pickle_load


class NuvoxModel:

    def __init__(self, config=None, keyboard=None):

        """

        Parameters
        ----------
        config: nuvox.config.model_config.ModelConfig
        keyboard: nuvox.keyboard.Keyboard
        """

        self.is_vocabulary_set = False
        self.config = config

        self.keyboard = keyboard

        self.keras_model = None

    def set_vocabulary(self, dataset):
        """
        set model vocabulary - this must be called before training
        Parameters
        ----------
        dataset
        """

        self.config.VOCAB = dataset.vocab
        self.config.VOCAB_SIZE = dataset.vocab_size
        self.config.WORD_TO_IDX = dataset.word_to_idx
        self.config.IDX_TO_WORD = {v: k for k, v in dataset.word_to_idx.items()}

        self.is_vocabulary_set = True

    def build_keras_model(self):
        model = Sequential()
        model.add(LSTM(units=100, input_shape=(self.config.MAX_SEQ_LEN, 2)))
        model.add(Dense(self.config.VOCAB_SIZE, activation='softmax'))
        model.compile(optimizer=self.config.OPTIMIZER, loss='categorical_crossentropy', metrics=['accuracy'])
        self.keras_model = model

    def train(self, dataset):
        """
        train model
        Parameters
        ----------
        dataset:
        """

        # If vocabulary of model has not already been set then do this now and build keras model
        if not self.is_vocabulary_set:
            self.set_vocabulary(dataset)
            self.build_keras_model()

        self.set_log_dir()  # set and create log dir

        self.save_model()

        batch_gen = self.batch_generator(dataset)

        steps_per_epoch = np.math.ceil(dataset.num_examples / self.config.BATCH_SIZE)
        
        callbacks = [TensorBoard(log_dir=self.config.LOG_DIR),
                     ModelCheckpoint(filepath=self.config.CHECKPOINT_PATH,
                                     monitor=self.config.METRIC_TO_MONITOR,
                                     save_best_only=True,
                                     save_weights_only=False)]

        self.keras_model.fit_generator(batch_gen,
                                       steps_per_epoch=steps_per_epoch,
                                       epochs=self.config.EPOCHS,
                                       callbacks=callbacks,
                                       verbose=1)

    def predict(self, trace):
        """ predict word from trace (list of (x,y) coords)
        Parameters
        ----------
        trace: list[tuples]
            list of (x,y) coordinates of trace

        Returns:
        predicted_text: str
            returns top predicted word for now
        """
        trace = np.array(trace)
        batch = np.zeros(shape=(self.config.MAX_SEQ_LEN, 2))
        batch[self.config.MAX_SEQ_LEN - trace.shape[0]:, :] = trace
        batch = np.expand_dims(batch, 0)  # add batch dim

        pred_probas = self.keras_model.predict_on_batch(batch)

        top_word_idx = np.argmax(pred_probas)
        top_word = self.config.IDX_TO_WORD[top_word_idx]

        return top_word

    def evaluate(self, dataset):

        steps = self.config.EVAL_EPOCHS * np.math.ceil(dataset.num_examples / self.config.BATCH_SIZE)
        batch_gen = self.batch_generator(dataset)

        loss, acc = self.keras_model.evaluate_generator(batch_gen, steps=steps)
        print('Evaluation: Loss {:.2f}  Accuracy: {:.1%}%'.format(loss, acc))

        return loss, acc

    def save_model(self):
        """
        """

        # Save model config
        pickle_save(os.path.join(self.config.LOG_DIR, 'model_config.pkl'), self.config)
        pickle_save(os.path.join(self.config.LOG_DIR, 'keyboard.pkl'), self.keyboard)

        self.keras_model.save(self.config.CHECKPOINT_PATH)

        print('Model weights and config saved in : {}'.format(self.config.LOG_DIR))

    def load_model(self, model_dir):

        self.config = pickle_load(os.path.join(model_dir, 'model_config.pkl'))
        self.keyboard = pickle_load(os.path.join(model_dir, 'keyboard.pkl'))

        self.keras_model = load_model(self.config.CHECKPOINT_PATH)

    def set_log_dir(self):

        if not os.path.isdir(self.config.OUTPUT_DIR):
            os.mkdir(self.config.OUTPUT_DIR)

        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.config.LOG_DIR = os.path.join(self.config.OUTPUT_DIR, timestamp)
        os.mkdir(self.config.LOG_DIR)

        self.config.CHECKPOINT_PATH = os.path.join(self.config.LOG_DIR, 'best_{}.h5'.format(self.config.METRIC_TO_MONITOR))

    def batch_generator(self, dataset):
        """
        generate batches for training
        Parameters
        ----------
        dataset: nuvox.dataset.Dataset

        Yields
        -------
        batch: np.ndarray
        labels: np.ndarray
        """
        iteration = 0
        num_examples = self.config.VOCAB_SIZE
        batch_size = self.config.BATCH_SIZE
        max_seq_len = self.config.MAX_SEQ_LEN
        shuffle = self.config.SHUFFLE

        batch = np.zeros(shape=(batch_size, max_seq_len, 2))  # (x, y) only for now
        labels = np.zeros(shape=(batch_size, dataset.vocab_size))

        while True:

            if iteration % num_examples == 0 and shuffle:
                random.shuffle(dataset.word_seq)

            word = dataset.word_seq[iteration % num_examples]
            trace = np.array(get_random_trace(self.keyboard, word))  # [seq_len, 2]
            label = to_categorical(dataset.word_to_idx[word], num_classes=dataset.vocab_size)  # one-hot

            if len(trace) > max_seq_len:
                raise Exception('trace exceeds maximum length: '.format(max_seq_len))

            batch[iteration % batch_size, max_seq_len - trace.shape[0]:, :] = trace
            labels[iteration % batch_size] = label

            if iteration % batch_size == batch_size -1:

                yield batch, labels

                batch = np.zeros(shape=(batch_size, max_seq_len, 2))  # (x, y) only for now
                labels = np.zeros(shape=(batch_size, dataset.vocab_size))

            iteration += 1


if __name__ == '__main__':

    model = NuvoxModel()
    model.load_model('../models/02_01_2020_10_03_26')

    trace = get_random_trace(model.keyboard, 'a')
    trace2 = get_random_trace(model.keyboard, 'the')
    pred = model.predict(trace)
    print('stop here')


