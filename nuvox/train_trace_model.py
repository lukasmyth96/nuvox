

from nuvox.config.model_config import ModelConfig
from nuvox.config.keyboard_config import nuvox_standard_keyboard
from nuvox.trace_model import TraceModel
from nuvox.keyboard import Keyboard
from nuvox.dataset import Dataset
from nuvox.utils.common import pickle_load


if __name__ == '__main__':

    model_config = ModelConfig()

    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)

    vocab = pickle_load(model_config.VOCAB_FILE)
    print('Removing words from vocab if they exceed length {}...'.format(model_config.MAX_WORD_LENGTH))
    vocab = [word for word in vocab if len(word) <= model_config.MAX_WORD_LENGTH]

    dataset = Dataset(keyboard)
    dataset.build_from_vocab(vocab)

    model = TraceModel(config=model_config, keyboard=keyboard)

    model.train(dataset)

    loss, acc = model.evaluate(dataset)
    print('\n\n Final Performance: train loss: {:.2f}  train accuracy: {:.1%}'.format(loss, acc))

