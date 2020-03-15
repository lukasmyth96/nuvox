
import tkinter as tk

from nuvox.keyboard import Keyboard
from nuvox.view import View
from nuvox.services.predictive_text import PredictiveText
from nuvox.services.text_to_speech import TextToSpeech
from nuvox.services.eye_gaze_server import EyeGazeServer


class Controller:

    def __init__(self, config):
        """

        Parameters
        ----------
        config: nuvox.config.Config
        """

        # Build Keyboard
        self.keyboard = Keyboard(key_list=config.KEY_LIST)

        # Build View
        self.root = tk.Tk()
        self.view = View(root=self.root)

        # Initialise services
        self.predictive_text = PredictiveText()
        self.text_to_speech = TextToSpeech()
        self.eye_gaze_server = EyeGazeServer()

