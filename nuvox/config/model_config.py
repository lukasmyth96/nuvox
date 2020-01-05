

class ModelConfig:

    # Training settings
    EPOCHS = 10000
    STEPS_PER_EPOCH = 50
    EVAL_EPOCHS = 10
    BATCH_SIZE = 32
    SHUFFLE = True
    OPTIMIZER = 'adam'
    MAX_SEQ_LEN = 250

    # Callbacks
    METRIC_TO_MONITOR = 'accuracy'
    SAVE_BEST_ONLY = True

    # Output
    OUTPUT_DIR = '../models/trace_models'
    LOG_DIR = None  # timestamped sub-dir created on fly during training
    CHECKPOINT_PATH = None

    # path to vocab file from which the dataset is built - should be a .pkl file containing a python list
    VOCAB_FILE = '/home/luka/PycharmProjects/nuvox/models/trace_models/vocab.pkl'

    # Trace
    TRACE_MIN_SEPARATION = 0.05
    ADD_GRADIENT_TO_TRACE = True
    TRACE_DIM = 2 + int(ADD_GRADIENT_TO_TRACE)

    VOCAB = None
    VOCAB_SIZE = None

    NUM_UNIQUE_REPR = None
    WORD_TO_DISCRETE_REPR = None  # dict mapping individual word to it's discrete representation
    DISCRETE_REPR_TO_WORDS = None  # dict mapping a unique discrete representation to a list of words that share that representation
    DISCRETE_REPR_TO_IDX = None
    IDX_TO_DISCRETE_REPR = None

