import random

import numpy as np

from nuvox.config.keyboard_config import nuvox_standard_keyboard
from nuvox.keyboard import Keyboard
from nuvox.traces import get_random_trace
from nuvox.dataset import Dataset

from keras.layers import Input, LSTM, TimeDistributed, Dense
from keras.models import  Sequential
from keras.utils import to_categorical


class NuvoxModel:

    def __init__(self):

        self.keyboard = Keyboard()
        self.keyboard.build_keyboard(nuvox_standard_keyboard)

        self.vocab_size = None
        self.max_seq_len = None

        self.keras_model = None

    def build_keras_model(self):
        model = Sequential()
        model.add(LSTM(units=100, input_shape=(self.max_seq_len, 2)))
        model.add(Dense(self.vocab_size, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.keras_model = model


def batch_generator(dataset, keyboard, batch_size, shuffle=True):
    """
    generate batches for training
    Parameters
    ----------
    dataset: nuvox.dataset.Dataset
    keyboard: nuvox.keyboard.Keyboard
    batch_size: int
    shuffle: bool

    Yields
    -------
    batch: np.ndarray
    labels: np.ndarray
    """
    iteration = 0
    num_examples = len(dataset.word_seq)
    maxlen = 50

    batch = np.zeros(shape=(batch_size, maxlen, 2))  # (x, y) only for now
    labels = np.zeros(shape=(batch_size, dataset.vocab_size))

    while True:

        if iteration % num_examples == 0 and shuffle:
            random.shuffle(dataset.word_seq)

        word = dataset.word_seq[iteration % num_examples]
        trace = np.array(get_random_trace(keyboard, word))  # [seq_len, 2]
        label = to_categorical(dataset.word_to_idx[word], num_classes=dataset.vocab_size)  # one-hot

        if len(trace) > maxlen:
            raise Exception('trace exceeds maximum length: '.format(maxlen))

        batch[iteration % batch_size, maxlen - trace.shape[0]:, :] = trace
        labels[iteration % batch_size] = label

        if iteration % batch_size == batch_size -1:

            yield batch, labels

            batch = np.zeros(shape=(batch_size, maxlen, 2))  # (x, y) only for now
            labels = np.zeros(shape=(batch_size, dataset.vocab_size))

        iteration += 1


if __name__ == '__main__':

    """ Training"""

    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)

    text = 'hello what is your name? mine is luka'
    dataset = Dataset()
    dataset.fit_on_text(text)

    model = NuvoxModel()

    batch_gen = batch_generator(dataset, keyboard, batch_size=3)

    model.vocab_size = dataset.vocab_size
    model.max_seq_len = 50
    model.build_keras_model()
    model.keras_model.fit_generator(batch_gen, epochs=100, steps_per_epoch=3)


    print('Stop here')


