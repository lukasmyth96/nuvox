

class ModelConfig:

    # Training settings
    EPOCHS = 10
    EVAL_EPOCHS = 50
    BATCH_SIZE = 32
    SHUFFLE = True
    OPTIMIZER = 'adam'
    MAX_SEQ_LEN = 200

    # Callbacks
    METRIC_TO_MONITOR = 'accuracy'
    SAVE_BEST_ONLY = True

    # Output
    OUTPUT_DIR = '../models'
    LOG_DIR = None  # timestamped sub-dir created on fly during training
    CHECKPOINT_PATH = None

    # Data settings - using this while only training on single words at a time
    NUM_WORDS_TO_TRAIN_ON = 100
    MIN_WORD_LEN = 3

    # Will be set before training
    VOCAB_SIZE = None
    VOCAB = None
    WORD_TO_IDX = None
    IDX_TO_WORD = None


