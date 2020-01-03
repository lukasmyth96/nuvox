

class ModelConfig:

    # Training settings
    EPOCHS = 10000
    EVAL_EPOCHS = 50
    BATCH_SIZE = 32
    SHUFFLE = True
    OPTIMIZER = 'adam'
    MAX_SEQ_LEN = 250

    # Callbacks
    METRIC_TO_MONITOR = 'accuracy'
    SAVE_BEST_ONLY = True

    # Output
    OUTPUT_DIR = '../models'
    LOG_DIR = None  # timestamped sub-dir created on fly during training
    CHECKPOINT_PATH = None

    # Data settings - using this while only training on single words at a time
    NUM_WORDS_TO_TRAIN_ON = 2500
    MIN_WORD_LEN = 1

    # Trace
    TRACE_MIN_SEPARATION = 0.05
    ADD_GRADIENT_TO_TRACE = True
    TRACE_DIM = 2 + int(ADD_GRADIENT_TO_TRACE)

    # Will be set before training
    VOCAB_SIZE = None
    VOCAB = None
    WORD_TO_IDX = None
    IDX_TO_WORD = None


