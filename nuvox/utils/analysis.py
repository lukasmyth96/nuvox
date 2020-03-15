from matplotlib import pyplot as plt

from nuvox.config.config import nuvox_standard_keyboard
from nuvox.legacy.keyboard import Keyboard

from nuvox.dataset import get_dataset_of_top_n_words


def get_theoretical_max_accuracy(keyboard, wordlist):
    """Calculate the theoretical maximum performance that a model can be expected to achieve by looking at the
    words that have the same path to trace

    Note: current implemenation assumes all words appear in the training text equally often
    """

    word_to_representation = {}
    for word in wordlist:
        try:
            word_to_representation[word] = keyboard.get_discrete_representation(word)
        except ValueError:
            continue

    # create reverse mapping from unique representations to list of words that have that representation
    representation_to_words = {}
    for word, representation in word_to_representation.items():
        if not representation_to_words.get(representation):
            representation_to_words[representation] = [word]
        else:
            representation_to_words[representation].append(word)

    theoretical_max = 0
    for repr, words in representation_to_words.items():
        theoretical_max += (1/len(wordlist)) / len(words)

    return theoretical_max


if __name__ == "__main__":
    """ Testing"""

    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)

    n_words = []
    theoretical_maxes = []
    print('Computing theoretical max accuracies...')

    n = 200000
    dataset = get_dataset_of_top_n_words(n)
    theoretical_max = get_theoretical_max_accuracy(keyboard, dataset.vocab)
    n_words.append(n)
    theoretical_maxes.append(theoretical_max)

    fig, ax = plt.subplots()
    ax.scatter(n_words, theoretical_maxes)
    ax.set_xlabel('Number of most frequent words in vocab')
    ax.set_ylabel('Theoretical Maximum Accuracy (%)')
    ax.set_title('Theoretical max accuracy vs number of words in vocabulary')
    plt.show()
