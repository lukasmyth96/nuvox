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
    REQ_DWELL_TIME = 2.0  # seconds required to start/stop a swype
    GAZE_INTERVAL = 0.1  # seconds between consecutive sampling of the gaze position

    # predictive text
    VOCAB_PATH = os.path.join(ROOT_DIR, 'config', 'discrete_representation_to_words.pkl')  # TODO compute this on fly

    # eye gaze server
    GAZE_SERVER_HOST = 'http://localhost:3070'
    EXE_PATH = os.path.join(ROOT_DIR, 'lib', 'Interaction_Streams_101.exe')

    # Audio
    TTS_SAMPLES_DIR = os.path.join(ROOT_DIR, 'tts_samples')

    # key settings
    FONT = 'calibri'
    FONT_SIZE = 10
    JUSTIFY = 'center'
    TEXT_COLOUR = (255, 255, 255)
    DEFAULT_BG = (32, 32, 32)  # default colour of key
    HIGHLIGHT_BG = (64, 0, 0)  # colour when key is fully selected
    START_KEY_COLOUR = (0, 100, 0)  # colour start key flashes to indicate start of a swype






