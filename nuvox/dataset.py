
from tqdm import tqdm


import nuvox


class Dataset:

    def __init__(self, keyboard):

        if not isinstance(keyboard, nuvox.keyboard.Keyboard):
            print('Parameter: keyboard must be an instance of nuvox.keyboard.Keyboard')
        self.keyboard = keyboard

        self.vocab = []
        self.vocab_size = 0
        self.num_unique_repr = 0

        self.word_to_discrete_repr = {}  # maps each word in vocab to the idx of it's discrete representation
        self.discrete_repr_to_words = {}  # maps idx of a discrete path representation to a list of words that share that path
        self.discrete_repr_to_idx = {}
        self.idx_to_discrete_repr = {}

        self.word_seq = []
        self.num_examples = 0

    def build_from_vocab(self, vocab):
        """ build dataset from vocab list"""

        self.vocab = vocab
        self.num_examples = len(self.vocab)
        self.vocab_size = len(self.vocab)

        print('Building dataset with vocab of {} words...'.format(self.vocab_size))
        for word in tqdm(self.vocab):

            discrete_repr = self.keyboard.get_discrete_representation(word)
            self.word_to_discrete_repr[word] = discrete_repr

            if discrete_repr in self.discrete_repr_to_words.keys():
                self.discrete_repr_to_words[discrete_repr].append(word)
            else:
                self.discrete_repr_to_words[discrete_repr] = [word]

        self.discrete_repr_to_idx = {rep: idx for idx, rep in enumerate(list(self.discrete_repr_to_words))}
        self.idx_to_discrete_repr = {idx: rep for rep, idx in self.discrete_repr_to_idx.items()}

        self.num_unique_repr = len(set(list(self.discrete_repr_to_idx)))



