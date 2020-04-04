import os

from nuvox.config.keyboard_layouts import nuvox_standard_keyboard
from definition import ROOT_DIR


class Config:

    # keyboard layout
    KEY_LIST = nuvox_standard_keyboard
    FIXED_KEY_ID_TO_PUNCTUATION = {'7': '.',
                                   '8': ',',
                                   '9': '?'}

    # display settings
    DISPLAY_HEIGHT = 600
    DISPLAY_WIDTH = 750

    DISPLAY_BG_COLOUR = 'steel blue'
    RESIZABLE = False
    FORCE_ON_TOP = True

    # swype settings
    REQ_DWELL_TIME = 1  # seconds required to start/stop a swype
    GAZE_INTERVAL = 0.1  # seconds between consecutive sampling of the gaze position

    # control settings
    CONTROL_WITH_EYES = True
    TIME_BEFORE_SWITCH_TO_MOUSE = 5  # secs without gaze data before asking to switch to mouse
    INTERVALS_BEFORE_SWITCH_TO_MOUSE = TIME_BEFORE_SWITCH_TO_MOUSE / GAZE_INTERVAL

    # predictive text
    VOCAB_PATH = os.path.join(ROOT_DIR, 'nuvox', 'config', 'top_25k_vocab.pkl')
    MAX_POTENTIAL_WORDS = 20  # maximum words passed to the language model for consideration
    PRED_FLASH_DURATION = 0.5  # num secs that predicted word is flashed on key
    KEYS_TO_IGNORE = ['5', ',', '.', '?', 'display', 'suggestion_1', 'suggestion_2', 'suggestion_3',
                      'speak', 'delete', 'clear', 'exit']

    # eye gaze server
    GAZE_SERVER_HOST = 'http://localhost:3070'
    EXE_PATH = os.path.join(ROOT_DIR, 'eye_gaze_server', 'Eye_Gaze_Server.exe')

    # key settings
    FONT = 'calibri'
    BUTTON_FONT_SIZE = 18
    DISPLAY_FONT_SIZE = 12
    JUSTIFY = 'center'
    TEXT_COLOUR = (255, 255, 255)
    DEFAULT_BG = (32, 32, 32)  # default colour of key
    HIGHLIGHT_BG = (64, 0, 0)  # colour when key is fully selected
    START_KEY_COLOUR = (0, 100, 0)  # colour start key flashes to indicate start of a swype






