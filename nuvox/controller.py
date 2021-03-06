import copy
import tkinter as tk

from nuvox.keyboard import Keyboard
from nuvox.views.main_view import View
from nuvox.services.predictive_text import PredictiveText
from nuvox.services.text_to_speech import TextToSpeech
from nuvox.services.eye_gaze_server import EyeGazeServer, NoGazeDataReturned
from nuvox.analytics.session import Session
from nuvox.swype import Swype
from nuvox.analytics.diagnostic_functions import plot_swype_probabilities

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
        self.session = Session(config=config)  # analytics session

        # Swype
        self.swype_in_progress = False
        self.required_iterations_in_focus = int(config.REQ_DWELL_TIME / config.GAZE_INTERVAL)
        self.key_trace = []
        self.current_text = ''
        self.suggestions = []  # list of all current suggestions
        self.suggestion_indices = []  # list of current indices being shown
        self.consecutive_intervals_with_no_gaze = 0  # used to automatically detect when to switch to mouse

        # Mapping form key_id to action functions
        self.key_id_to_action_function = {'speak': self.on_speak_key,
                                          'delete': self.on_del_key,
                                          'clear': self.on_clear_key,
                                          'exit': self.on_exit_key,
                                          'suggestion_1': lambda: self.on_suggestion_key(1),
                                          'suggestion_2': lambda: self.on_suggestion_key(2),
                                          'suggestion_3': lambda: self.on_suggestion_key(3),
                                          'suggestion_left_arrow': lambda: self.on_suggestion_left_arrow(),
                                          'suggestion_right_arrow': lambda: self.on_suggestion_right_arrow()
                                          }

    @property
    def key_in_focus_just_changed(self):
        return (len(self.key_trace) >= 2) and (self.key_trace[-1] != self.key_trace[-2])

    @property
    def key_in_focus_for_required_time(self):
        req_iters = self.required_iterations_in_focus
        return (len(self.key_trace) >= req_iters) and (len(set(self.key_trace[-req_iters:])) == 1)

    def run_app(self):
        if self.config.CONTROL_WITH_EYES:
            self.eye_gaze_server.start_server()
        self.view.start_loop()

    def periodic_callback(self):
        """
        Called every interval - gets eye gaze coords and adds to key list
        """
        try:
            relx, rely = self.get_gaze_relative_to_window()
            self.consecutive_intervals_with_no_gaze = 0

            key_in_focus = self.keyboard.get_key_at_point(x=relx, y=rely)
            if key_in_focus:
                self.key_trace.append(key_in_focus.key_id)

                if self.key_in_focus_just_changed:
                    self.on_key_in_focus_changing()
                else:
                    self.view.increment_widget_colour(key_id=key_in_focus.key_id)
                    if self.key_in_focus_for_required_time:
                        self.on_key_in_focus_for_required_time(key_in_focus)

        except NoGazeDataReturned:
            self.consecutive_intervals_with_no_gaze += 1
            if self.consecutive_intervals_with_no_gaze > self.config.INTERVALS_BEFORE_SWITCH_TO_MOUSE:
                switch_to_mouse = self.view.open_yes_no_popup(message='Failed to detect eye gaze - switch to mouse control?')
                if switch_to_mouse:
                    self.config.CONTROL_WITH_EYES = False
                else:
                    self.consecutive_intervals_with_no_gaze = -100000

            self.on_gaze_leaving_window()

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
        current_key_trace = copy.copy(self.key_trace)  # as it will change whilst processing
        swype = Swype(key_trace=current_key_trace)
        self.swype_in_progress = False
        ranked_suggestions = self.predictive_text.predict_next_word(prompt=self.current_text, swype=swype)
        if ranked_suggestions:
            swype.ranked_suggestions = ranked_suggestions
            swype.accepted_word = ranked_suggestions[0]

            # FIXME delete after debugging
            #plot_swype_probabilities(swype, top_n=self.config.MAX_SUGGESTIONS)

            self.session.append(swype)
            self.update_display_text(' '.join([self.current_text, ranked_suggestions[0]]))
            self.update_suggestions(suggestions=ranked_suggestions[1:],
                                    suggestion_indices=list(range(min(3, len(ranked_suggestions[1:])))))
            self.view.flash_pred_word(key_id=key_in_focus.key_id, word=ranked_suggestions[0])
        self.view.reset_widget_colour(key_id=key_in_focus.key_id)
        self.key_trace.clear()

    def on_gaze_leaving_window(self):
        if self.key_trace:
            self.view.reset_widget_colour(key_id=self.key_trace[-1])

    def on_speak_key(self):
        self.text_to_speech.speak_text(text=self.current_text)

    def on_exit_key(self):
        answered_yes = self.view.open_yes_no_popup(message='Are you sure you want to exit?')
        if answered_yes:
            self.session.save()  # save analytics data
            self.view.toplevel.destroy()
            try:
                self.eye_gaze_server.process.kill()
            except AttributeError:
                pass

    def on_del_key(self):
        self.session.swypes[-1].was_deleted = True
        current_words = self.current_text.split(' ')
        if current_words:
            self.update_display_text(' '.join(current_words[:-1]))

    def on_clear_key(self):
        self.update_display_text(text='')
        self.update_suggestions(suggestions=['']*3, suggestion_indices=[])

    def update_display_text(self, text):
        if text and (text[-1] in self.config.FIXED_KEY_ID_TO_PUNCTUATION.values()):
            text = ''.join([text[:-2], text[-1]])  # filter space before punc e.g. 'hello .' --> 'hello.'
        self.current_text = text
        self.view.update_display_text(new_text=text)

    def on_suggestion_key(self, suggestion_num):
        current_words = self.current_text.split(' ')
        widget = self.view.key_id_to_widget['suggestion_{}'.format(suggestion_num)]
        suggestion = widget.cget('text')
        self.session.swypes[-1].accepted_word = suggestion  # update accepted word in analytics session
        new_words = current_words[:-1] + [suggestion]
        self.update_display_text(text=' '.join(new_words))

    def on_suggestion_right_arrow(self):
        if self.suggestion_indices:
            scroll_amount = min(3, len(self.suggestions)-self.suggestion_indices[-1]-1)
            self.update_suggestions(suggestions=self.suggestions, suggestion_indices=[i+scroll_amount for i in self.suggestion_indices])

    def on_suggestion_left_arrow(self):
        if self.suggestion_indices and self.suggestion_indices[0] >= 3:
            self.update_suggestions(suggestions=self.suggestions,suggestion_indices=[i - 3 for i in self.suggestion_indices])

    def update_suggestions(self, suggestions, suggestion_indices):
        """
        Parameters
        ----------
        suggestions: list[str]
        suggestion_indices: list[int]
        """
        self.suggestions = suggestions
        self.suggestion_indices = suggestion_indices
        for display_idx, suggestion_idx in enumerate(suggestion_indices):
            widget = self.view.key_id_to_widget.get('suggestion_{}'.format(display_idx+1))
            if widget:
                widget.configure(text=suggestions[suggestion_idx])

    def get_gaze_relative_to_window(self):
        top_level = self.view.toplevel
        if self.config.CONTROL_WITH_EYES:
            x, y = self.eye_gaze_server.get_gaze_relative_to_screen()
        else:
            x, y = self.get_mouse_position_relative_to_screen()

        # get coords relative to toplevel window
        relx = (x * top_level.winfo_screenwidth() - top_level.winfo_x()) / top_level.winfo_width()
        rely = (y * top_level.winfo_height() - top_level.winfo_y()) / top_level.winfo_height()
        return relx, rely

    def get_mouse_position_relative_to_screen(self):
        top_level = self.view.toplevel
        x = top_level.winfo_pointerx() / top_level.winfo_screenwidth()
        y = top_level.winfo_pointery() / top_level.winfo_screenheight()
        return x, y



