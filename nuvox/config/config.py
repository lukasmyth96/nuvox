import os

from nuvox.config.keyboard_layouts import nuvox_standard_keyboard
from definition import ROOT_DIR


class Config:

    # keyboard layout
    KEY_LIST = nuvox_standard_keyboard

    # display settings
    DISPLAY_WIDTH = 450
    DISPLAY_HEIGHT = 600
    DISPLAY_BG_COLOUR = 'steel blue'
    RESIZABLE = False
    FORCE_ON_TOP = True

    # swype settings
    REQ_DWELL_TIME = 0.8  # seconds required to start/stop a swype
    GAZE_INTERVAL = 0.05  # seconds between consecutive sampling of the gaze position

    # control settings
    CONTROL_WITH_EYES = True
    TIME_BEFORE_SWITCH_TO_MOUSE = 5  # secs without gaze data before asking to switch to mouse
    INTERVALS_BEFORE_SWITCH_TO_MOUSE = TIME_BEFORE_SWITCH_TO_MOUSE / GAZE_INTERVAL

    # predictive text
    VOCAB_PATH = os.path.join(ROOT_DIR, 'nuvox', 'config', 'discrete_representation_to_words.pkl')  # TODO compute this on fly?
    MAX_POTENTIAL_WORDS = 5  # maximum words passed to the language model for consideration
    PRED_FLASH_DURATION = 0.5  # num secs that predicted word is flashed on key

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






