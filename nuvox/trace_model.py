import os
from datetime import datetime
import pickle
import random


import numpy as np
from tensorflow.keras.callbacks import Callback

# noinspection PyUnresolvedReferences
from tensorflow.keras.layers import Input, Masking, LSTM, Dense
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping

from nuvox.traces import get_random_trace, add_gradients_to_trace
from nuvox.utils.common import pickle_save, pickle_load


class TraceModel:

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

        self.encoder_model = None
        self.decoder_model = None
        self.training_model = None

    def set_vocabulary(self, dataset):
        """
        set model vocabulary - this must be called before model can be built
        Parameters
        ----------
        dataset
        """

        self.config.VOCAB = dataset.vocab
        self.config.VOCAB_SIZE = dataset.vocab_size
        self.config.NUM_UNIQUE_REPR = dataset.num_unique_repr

        self.config.WORD_TO_DISCRETE_REPR = dataset.word_to_discrete_repr
        self.config.DISCRETE_REPR_TO_WORDS = dataset.discrete_repr_to_words
        self.config.DISCRETE_REPR_TO_IDX = dataset.discrete_repr_to_idx
        self.config.IDX_TO_DISCRETE_REPR = dataset.idx_to_discrete_repr

        self.is_vocabulary_set = True

    def build_keras_models(self):
        """ Build encoder, decoder and combined training model"""
        # define training encoder
        encoder_inputs = Input(shape=(self.config.MAX_SEQ_LEN, self.config.TRACE_DIM))
        masking = Masking()(encoder_inputs)
        encoder = LSTM(self.config.LSTM_UNITS, return_state=True)
        encoder_outputs, state_h, state_c = encoder(masking)
        encoder_states = [state_h, state_c]

        # define training decoder
        decoder_inputs = Input(shape=(None, self.config.OUTPUT_DIM))
        decoder_lstm = LSTM(self.config.LSTM_UNITS, return_sequences=True, return_state=True)
        decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
        decoder_dense = Dense(self.config.OUTPUT_DIM, activation='softmax')
        decoder_outputs = decoder_dense(decoder_outputs)
        training_model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

        # define inference encoder
        encoder_model = Model(encoder_inputs, encoder_states)

        # define inference decoder
        decoder_state_input_h = Input(shape=(self.config.LSTM_UNITS,))
        decoder_state_input_c = Input(shape=(self.config.LSTM_UNITS,))
        decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
        decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs, initial_state=decoder_states_inputs)
        decoder_states = [state_h, state_c]
        decoder_outputs = decoder_dense(decoder_outputs)
        decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)

        self.training_model = training_model
        self.encoder_model = encoder_model
        self.decoder_model = decoder_model

    def compile_training_model(self):
        """ compile training model"""
        if self.training_model is None:
            raise Exception('You must call build_keras_models before you can compile them')

        self.training_model.compile(loss='categorical_crossentropy', optimizer=self.config.OPTIMIZER, metrics=['accuracy'])

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
            self.build_keras_models()
            self.compile_training_model()

        self.set_log_dir()  # set and create log dir

        self.save_model()  # call once before training to ensure keyboard and model config are saved

        batch_gen = self.batch_generator(dataset)

        if self.config.STEPS_PER_EPOCH is not None:
            steps_per_epoch = self.config.STEPS_PER_EPOCH
        else:
            steps_per_epoch = np.math.ceil(dataset.num_examples / self.config.BATCH_SIZE)
        
        callbacks = [TensorBoard(log_dir=self.config.LOG_DIR, profile_batch=0),
                     ModelCheckpoint(filepath=self.config.TRAINING_MODEL_PATH,
                                     monitor=self.config.METRIC_TO_MONITOR,
                                     save_best_only=True,
                                     save_weights_only=False),
                     SubModelCheckpoint(model=self.encoder_model,
                                        filepath=self.config.ENCODER_PATH,
                                        monitor=self.config.METRIC_TO_MONITOR),
                     SubModelCheckpoint(model=self.decoder_model,
                                        filepath=self.config.DECODER_PATH,
                                        monitor=self.config.METRIC_TO_MONITOR)]

        self.training_model.fit_generator(batch_gen,
                                          steps_per_epoch=steps_per_epoch,
                                          epochs=self.config.EPOCHS,
                                          callbacks=callbacks,
                                          verbose=1)

        print('Training Complete')


    # def predict(self, trace, beam_width=5, min_return_confidence=0.1):
    #     """ predict word from trace (list of (x,y) coords)
    #     Parameters
    #     ----------
    #     trace: list[tuples]
    #         list of (x,y) coordinates of trace
    #     beam_width: int
    #         the number of words to return
    #     min_return_confidence: float
    #         minimum confidence required in order to return a predicted word
    #
    #     Returns:
    #     --------
    #     possible_words: list[str]
    #         possible words to top n most likely paths
    #     """
    #
    #     if self.config.TRACE_DIM == 3:
    #         trace = add_gradients_to_trace(trace)
    #
    #     trace = np.array(trace)
    #     batch = np.zeros(shape=(self.config.MAX_SEQ_LEN, self.config.TRACE_DIM))
    #     batch[(self.config.MAX_SEQ_LEN - trace.shape[0]):] = trace
    #     batch = np.expand_dims(batch, 0)  # add batch dim
    #
    #     # get trace encoding
    #     state = self.encoder_model.predict(batch)
    #
    #     # maintain a list of top n sequences so far
    #     top_sequences_so_far = [self.config.START_OF_SEQ_TOKEN] * beam_width
    #
    #     # get initial decoder_input
    #     decoder_input = np.zeros(shape=(1, self.config.MAX_OUTPUT_LENGTH, self.config.OUTPUT_DIM))
    #     decoder_input[0, 0] = to_categorical(self.config.START_OF_SEQ_TOKEN, num_classes=self.config.OUTPUT_DIM)
    #
    #     def get_new_top_sequences(top_sequences_so_far, current_state, time_step, beam_width):
    #         """
    #
    #         Parameters
    #         ----------
    #         decoder_input
    #         current_state
    #         time_step
    #         beam_width
    #
    #         Returns
    #         -------
    #
    #         """
    #         yhat, h, c = self.decoder_model.predict([decoder_input] + current_state)
    #         for example_idx, pred in enumerate(yhat):
    #             next_word_probs = pred[time_step]
    #             top_n_indices = next_word_probs.argsort()[-beam_width:][::-1]
    #             top_n_probs = [next_word_probs[idx] for idx in top_n_indices]
    #
    #         return top_n_indices, top_n_probs, [h, c]
    #
    #
    #
    #     for t in range(self.config.MAX_OUTPUT_LENGTH):
    #         # predict next char
    #         yhat, h, c = self.decoder_model.predict([decoder_input] + state)
    #
    #         # store prediction
    #         pred_probas[t] = (yhat[0, t, :])
    #
    #         # update decoder intput
    #         top_pred_idx = np.argmax(yhat[0, t])
    #
    #         if top_pred_idx == self.config.END_OF_SEQ_TOKEN:
    #             break
    #         else:
    #             pred_tokens.append(top_pred_idx)
    #             decoder_input[0, t+1] = to_categorical(top_pred_idx, num_classes=self.config.OUTPUT_DIM)
    #
    #         # update state for next time-step
    #         state = [h, c]
    #
    #     return pred_tokens

    def evaluate(self, dataset):

        steps = self.config.EVAL_EPOCHS * np.math.ceil(dataset.num_examples / self.config.BATCH_SIZE)
        batch_gen = self.batch_generator(dataset)

        loss, acc = self.training_model.evaluate_generator(batch_gen, steps=steps)
        print('Evaluation: Loss {:.2f}  Accuracy: {:.1%}%'.format(loss, acc))

        return loss, acc

    def save_model(self):
        """
        """

        # Save model config
        pickle_save(os.path.join(self.config.LOG_DIR, 'model_config.pkl'), self.config)
        pickle_save(os.path.join(self.config.LOG_DIR, 'keyboard.pkl'), self.keyboard)

        model_dir = self.config.LOG_DIR
        self.encoder_model.save(self.config.ENCODER_PATH)
        self.decoder_model.save(self.config.DECODER_PATH)
        self.training_model.save(self.config.TRAINING_MODEL_PATH)

        print('Model weights and config saved in : {}'.format(model_dir))

    def load_model(self, model_dir):

        self.config = pickle_load(os.path.join(model_dir, 'model_config.pkl'))
        self.keyboard = pickle_load(os.path.join(model_dir, 'keyboard.pkl'))

        # not using CHECKPOINT_PATH only because I might rename the model dir
        self.encoder_model = load_model(self.config.ENCODER_PATH)
        self.decoder_model = load_model(self.config.DECODER_PATH)
        self.training_model = load_model(self.config.TRAINING_MODEL_PATH)

    def set_log_dir(self):

        if not os.path.isdir(self.config.OUTPUT_DIR):
            os.mkdir(self.config.OUTPUT_DIR)

        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.config.LOG_DIR = os.path.join(self.config.OUTPUT_DIR, timestamp)
        os.mkdir(self.config.LOG_DIR)

        self.config.ENCODER_PATH = os.path.join(self.config.LOG_DIR, 'encoder_best_{}.h5'.format(self.config.METRIC_TO_MONITOR))
        self.config.DECODER_PATH = os.path.join(self.config.LOG_DIR, 'decoder_best_{}.h5'.format(self.config.METRIC_TO_MONITOR))
        self.config.TRAINING_MODEL_PATH = os.path.join(self.config.LOG_DIR, 'training_model_best_{}.h5'.format(self.config.METRIC_TO_MONITOR))

    def batch_generator(self, dataset):
        """
        generate batches for training
        Parameters
        ----------
        dataset: nuvox.dataset.Dataset

        Yields
        -------
        batch: list[np.ndarray]
        decoder_target: np.ndarray
        """
        iteration = 0
        num_examples = self.config.VOCAB_SIZE
        batch_size = self.config.BATCH_SIZE
        max_seq_len = self.config.MAX_SEQ_LEN
        shuffle = self.config.SHUFFLE

        encoder_input = np.zeros(shape=(batch_size, max_seq_len, self.config.TRACE_DIM))  # (x, y) only for now
        decoder_input = np.zeros(shape=(batch_size, self.config.MAX_OUTPUT_LENGTH, self.config.OUTPUT_DIM))
        decoder_target = np.zeros(shape=(batch_size, self.config.MAX_OUTPUT_LENGTH, self.config.OUTPUT_DIM))

        while True:

            if iteration % num_examples == 0 and shuffle:
                random.shuffle(dataset.vocab)

            word = dataset.vocab[iteration % num_examples]

            # Create encoder input
            trace = np.array(get_random_trace(self.keyboard,
                                              word,
                                              add_gradients=self.config.ADD_GRADIENT_TO_TRACE,
                                              min_dist_between_points=self.config.TRACE_MIN_SEPARATION))

            if len(trace) > max_seq_len:
                raise Exception('trace exceeds maximum length: '.format(max_seq_len))

            encoder_input[iteration % batch_size, (self.config.MAX_SEQ_LEN - trace.shape[0]):] = trace

            discrete_repr = self.config.WORD_TO_DISCRETE_REPR[word]
            discrete_repr = list(discrete_repr)  # convert string of chars to list
            # Pad target sequence with end of sequence tokens to meet max output length
            while len(discrete_repr) < self.config.MAX_OUTPUT_LENGTH:
                discrete_repr.append(self.config.END_OF_SEQ_TOKEN)

            # Create decoder target
            decoder_target[iteration % batch_size] = np.stack([to_categorical(token, num_classes=self.config.OUTPUT_DIM)
                                                               for token in discrete_repr])

            # Create decoder training input which is target shifted one place right with a start token at idx 1
            discrete_repr.pop()
            discrete_repr.insert(0, self.config.START_OF_SEQ_TOKEN)
            decoder_input[iteration % batch_size] = np.stack([to_categorical(token, num_classes=self.config.OUTPUT_DIM)
                                                              for token in discrete_repr])

            if iteration % batch_size == batch_size -1:

                yield [encoder_input, decoder_input], decoder_target

                encoder_input = np.zeros(shape=(batch_size, max_seq_len, self.config.TRACE_DIM))  # (x, y) only for now
                decoder_input = np.zeros(shape=(batch_size, self.config.MAX_OUTPUT_LENGTH, self.config.OUTPUT_DIM))
                decoder_target = np.zeros(shape=(batch_size, self.config.MAX_OUTPUT_LENGTH, self.config.OUTPUT_DIM))

            iteration += 1


class SubModelCheckpoint(Callback):
    """ Custom version of ModelCheckpoint to allow saving of encoder and decoder separatley"""
    def __init__(self, model, filepath, monitor):
        self.monitor = monitor
        if 'acc' in monitor:
            self.monitor_op = np.greater
            self.best = 0
        elif 'loss' in monitor:
            self.monitor_op = np.less
            self.best = np.Inf
        else:
            raise ValueError('Metric {} does not contain acc or loss'.format(monitor))

        self.filepath = filepath
        self.encoder = model

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor)
        if self.monitor_op(current, self.best):
            self.best = current
            self.model.save(self.filepath, overwrite=True)



if __name__ == '__main__':
    """ Testing predictions"""

    model_dir = '/home/luka/PycharmProjects/nuvox/models/trace_models/11_01_2020_15_13_43'
    model = TraceModel()
    model.load_model(model_dir)
    word = 'hello'
    trace = get_random_trace(model.keyboard, word, add_gradients=False)
    pred = model.predict(trace)
    print('stop here')


