

class ModelConfig:

    # Architecture settings
    OUTPUT_DIM = 12  # 9 keys + pad token (0) + start token (10) + end token (11)
    LSTM_UNITS = 100
    MAX_OUTPUT_LENGTH = 12
    OUTPUT_PAD_TOKEN = 0
    END_OF_SEQ_TOKEN = 11  # TODO these probably shouldn't be fixed as depend on number of keys in keyboard
    START_OF_SEQ_TOKEN = 10

    # Training settings
    EPOCHS = 10000
    STEPS_PER_EPOCH = 100
    EVAL_EPOCHS = 10
    BATCH_SIZE = 32
    SHUFFLE = True
    OPTIMIZER = 'adam'
    MAX_SEQ_LEN = 200  # max length of trace

    # Callbacks
    METRIC_TO_MONITOR = 'accuracy'
    SAVE_BEST_ONLY = True

    # Output
    OUTPUT_DIR = '../models/trace_models'
    LOG_DIR = None  # timestamped sub-dir created on fly during training
    ENCODER_PATH = None
    DECODER_PATH = None
    TRAINING_MODEL_PATH = None

    # path to vocab file from which the dataset is built - should be a .pkl file containing a python list
    VOCAB_FILE = '/home/luka/PycharmProjects/nuvox/models/trace_models/vocab.pkl'
    MAX_WORD_LENGTH = 10  # words exceeding this length will be removed from vocabulary

    # Trace
    TRACE_MIN_SEPARATION = 0.05
    ADD_GRADIENT_TO_TRACE = True
    TRACE_DIM = 2 + int(ADD_GRADIENT_TO_TRACE)

    # The following values will be assigned during trainign
    VOCAB = None
    VOCAB_SIZE = None

    NUM_UNIQUE_REPR = None
    WORD_TO_DISCRETE_REPR = None  # dict mapping individual word to it's discrete representation
    DISCRETE_REPR_TO_WORDS = None  # dict mapping a unique discrete representation to a list of words that share that representation
    DISCRETE_REPR_TO_IDX = None
    IDX_TO_DISCRETE_REPR = None

