
import tkinter as tk

from nuvox.keyboard import Keyboard
from nuvox.view import View
from nuvox.services.predictive_text import PredictiveText
from nuvox.services.text_to_speech import TextToSpeech
from nuvox.services.eye_gaze_server import EyeGazeServer, NoGazeDataReturned


class Controller:

    def __init__(self, config):
        """

        Parameters
        ----------
        config: nuvox.config.Config
        """
        self.config = config

        # Build Keyboard
        self.keyboard = Keyboard(key_list=config.KEY_LIST)

        # Build View
        self.root = tk.Tk()
        self.view = View(config=config)
        self.view.periodic_callback = self.periodic_callback
        self.view.create_widgets(keyboard=self.keyboard)

        # Initialise services
        self.predictive_text = PredictiveText(config=config)
        self.text_to_speech = TextToSpeech()
        self.eye_gaze_server = EyeGazeServer(host=config.GAZE_SERVER_HOST,
                                             exe_path=config.EXE_PATH)

        # Swype
        self.swype_in_progress = False
        self.required_iterations_in_focus = int(config.REQ_DWELL_TIME / config.GAZE_INTERVAL)
        self.key_trace = []
        self.current_text = ''

        # Mapping form key_id to action functions
        self.key_id_to_action_function = {'speak': self.on_speak_key,
                                          'delete': self.on_del_key,
                                          'clear': self.on_clear_key,
                                          'exit': self.on_exit_key,
                                          ',': lambda: self.on_punctuation_key(','),
                                          '.': lambda: self.on_punctuation_key('.'),
                                          '?': lambda: self.on_punctuation_key('?'),
                                          'suggestion_1': lambda: self.on_suggestion_key(1),
                                          'suggestion_2': lambda: self.on_suggestion_key(2),
                                          'suggestion_3': lambda: self.on_suggestion_key(3),
                                          }

    @property
    def key_in_focus_just_changed(self):
        return (len(self.key_trace) >= 2) and (self.key_trace[-1] != self.key_trace[-2])

    @property
    def key_in_focus_for_required_time(self):
        req_iters = self.required_iterations_in_focus
        return (len(self.key_trace) >= req_iters) and (len(set(self.key_trace[-req_iters:])) == 1)

    def run_app(self):
        self.eye_gaze_server.start_server()
        self.view.start_loop()

    def periodic_callback(self):
        """
        Called every interval - gets eye gaze coords and adds to key list
        """
        try:
            relx, rely = self.get_gaze_relative_to_window()
        except NoGazeDataReturned:
            self.on_gaze_leaving_window()
            return

        key_in_focus = self.keyboard.get_key_at_point(x=relx, y=rely)
        if key_in_focus:

            print('key in focus is: ', key_in_focus.key_id)

            self.key_trace.append(key_in_focus.key_id)

            if self.key_in_focus_just_changed:
                self.on_key_in_focus_changing()
            else:
                self.view.increment_widget_colour(key_id=key_in_focus.key_id)

            if self.key_in_focus_for_required_time:
                self.on_key_in_focus_for_required_time(key_in_focus)

        else:
            self.on_gaze_leaving_window()  # FIXME this should never really happen

    def on_key_in_focus_changing(self):
        prev_key_id, new_key_id = self.key_trace[-2:]
        self.view.reset_widget_colour(key_id=prev_key_id)
        self.view.increment_widget_colour(key_id=new_key_id)

    def on_key_in_focus_for_required_time(self, key_in_focus):

        if self.swype_in_progress:
            self.on_swype_end(key_in_focus)
        else:
            self.on_swype_start(key_in_focus)

    def on_swype_start(self, key_in_focus):
        key_action_function = self.key_id_to_action_function.get(key_in_focus.key_id)
        if key_action_function:
            key_action_function()
            self.key_trace.clear()
        else:
            self.key_trace = self.key_trace[-1:]
            self.view.change_widget_colour(key_id=key_in_focus.key_id, rgb=self.config.START_KEY_COLOUR)
            self.swype_in_progress = True

    def on_swype_end(self, key_in_focus):
        self.swype_in_progress = False
        ranked_predictions = self.predictive_text.predict_next_word(prompt=self.current_text,
                                                                    key_id_sequence=self.key_trace)
        if ranked_predictions:
            self.update_display_text(' '.join([self.current_text, ranked_predictions[0]]))
            self.update_suggestions(suggestions=ranked_predictions[1:])
            self.view.flash_pred_word(key_id=key_in_focus.key_id, word=ranked_predictions[0])
        self.view.reset_widget_colour(key_id=key_in_focus.key_id)
        self.key_trace.clear()

    def on_gaze_leaving_window(self):
        if self.key_trace:
            self.view.reset_widget_colour(key_id=self.key_trace[-1])

    def on_speak_key(self):
        self.text_to_speech.speak_text_in_new_thread(text=self.current_text)

    def on_exit_key(self):
        self.view.root.destroy()
        self.eye_gaze_server.process.kill()

    def on_del_key(self):
        current_words = self.current_text.split(' ')
        if current_words:
            self.update_display_text(' '.join(current_words[:-1]))

    def on_clear_key(self):
        self.update_display_text(text='')
        self.update_suggestions(suggestions=['']*3)

    def on_suggestion_key(self, suggestion_num):
        current_words = self.current_text.split(' ')
        widget = self.view.key_id_to_widget['suggestion_{}'.format(suggestion_num)]
        suggestion = widget.cget('text')
        new_words = current_words[:-1] + [suggestion]
        self.update_display_text(text=' '.join(new_words))

    def on_punctuation_key(self, char):
        self.update_display_text(''.join([self.current_text, char]))

    def update_display_text(self, text):
        self.current_text = text
        self.view.update_display_text(new_text=text)

    def update_suggestions(self, suggestions):
        # FIXME make number of suggestions configurable
        for idx, suggestion in enumerate(suggestions[:3]):
            widget = self.view.key_id_to_widget.get('suggestion_{}'.format(idx+1))
            if widget:
                widget.configure(text=suggestion)

    def get_gaze_relative_to_window(self):
        x, y = self.eye_gaze_server.get_gaze_relative_to_screen()
        root = self.view.root
        relx = (x * root.winfo_screenwidth() - root.winfo_x()) / root.winfo_width()
        rely = (y * root.winfo_height() - root.winfo_y()) / root.winfo_height()
        return relx, rely


