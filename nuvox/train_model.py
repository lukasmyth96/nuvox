

from nuvox.config.model_config import ModelConfig
from nuvox.config.keyboard_config import nuvox_standard_keyboard
from nuvox.model import NuvoxModel
from nuvox.keyboard import Keyboard
from nuvox.dataset import Dataset, get_dataset_of_top_n_words


if __name__ == '__main__':

    model_config = ModelConfig()

    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)

    dataset = get_dataset_of_top_n_words(n=model_config.NUM_WORDS_TO_TRAIN_ON, min_length=model_config.MIN_WORD_LEN)

    model = NuvoxModel(config=model_config, keyboard=keyboard)

    model.train(dataset)

    loss, acc = model.evaluate(dataset)
    print('\n\n Final Performance: train loss: {:.2f}  train accuracy: {:.1%}'.format(loss, acc))

