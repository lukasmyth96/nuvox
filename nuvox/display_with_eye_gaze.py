from collections import deque
import os
import subprocess
import time

import numpy as np
from tkinter import *

from definition import ROOT_DIR
import nuvox
from nuvox.trace_model import TraceModel
from nuvox.language_model import GPT2
from nuvox.utils.text_to_speech import TextToSpeech
from nuvox.utils.sound_effects import SFX
from nuvox.utils.interval_callback import IntervalCallback
from nuvox.get_eye_coordinates import get_eye_coords_relative_to_screen, NoGazeDataReturned


class Display:

    def __init__(self, keyboard, display_width, display_height):

        """
        Encapsulates the Keyboard display
        Parameters
        ----------
        keyboard: nuvox.keyboard.Keyboard
            keyboard object containing information about the keyboard layout and contents of each key
        display_width: int
            width of display in pixels
        display_height: int
            height of display in pixels
        """

        self.keyboard = keyboard
        self.display_width = display_width
        self.display_height = display_height

        self.trace_model = None
        self.language_model = None
        self.beam_width = 5

        self.gaze_server_process = None

        self.gui = Tk()
        self.gui.configure(background="steel blue")
        self.gui.title("nuvox keyboard")
        self.gui.geometry("{}x{}+{}+{}".format(self.display_width, self.display_height, 360, 50))
        self.gui.resizable(width=False, height=False)
        self.gui.attributes("-topmost", True)

        # For swype controls
        self.current_key_in_focus = None  # track the id of the key currently in focus
        self.required_time_in_focus = 2.0  # number of ms a key has to be hovered on before record_mouse_trace is toggled
        self.interval_secs = 0.1

        # key timer keeps track of how long the current key has been in focus for
        self.key_timer = IntervalCallback(interval=self.interval_secs,
                                          num_intervals=np.math.ceil(self.required_time_in_focus / self.interval_secs),
                                          completion_callback=self.on_single_key_in_focus_for_required_time,
                                          interval_callback=self.on_every_interval_a_key_is_in_focus)
        self.key_timer.start()

        self.record_eye_trace = False  # Flag to keep track of whether mouse movements should be recorded currently

        # Controlling colours of keys
        self.default_fg = (255, 255, 255)
        self.initial_bg = (32, 32, 32)
        self.final_bg = (64, 0, 0)
        number_colour_increments = np.math.ceil(self.required_time_in_focus / self.interval_secs)
        self.rgb_increment = tuple([int(val) for val in ((np.array(self.final_bg) - np.array(self.initial_bg)) / number_colour_increments)])

        # dict mapping key_id to TK object
        self.key_id_to_widget = {}

        # dict mapping key_id to nuvox.keyboard.Key object
        self.key_id_to_key_object = {}

        self.mouse_trace_buffer = deque(maxlen=200)  # store coordinates of mouse in buffer of fixed length
        self.trace_labels = []  # store label objects for trace

        self.build_display()

    def build_display(self):
        """ Build gui from information in keyboard object"""
        for key in self.keyboard.keys:

            if key.type in ['text_key', 'punctuation_key', 'null_key']:
                text = ' '.join(key.contents).upper()
                obj = self._create_button_object(master=self.gui, text=text)

            elif key.type == 'speak_button':
                obj = self._create_button_object(master=self.gui, text=' '.join(key.contents).upper(), command=self.press_speak)

            elif key.type == 'delete_button':
                obj = self._create_button_object(master=self.gui, text=' '.join(key.contents).upper(), command=self.press_delete)

            elif key.type == 'clear_button':
                obj = self._create_button_object(master=self.gui, text=' '.join(key.contents).upper(), command=self.clear_display)

            elif key.type == 'exit_button':
                obj = self._create_button_object(master=self.gui, text=' '.join(key.contents).upper(), command=self.exit)

            elif key.type == 'display_frame':
                idx = int(key.key_id[-1])  # TODO find better way of getting display box idx
                selection_callback = lambda idx: lambda: self.pick_from_prediction_list(idx)
                obj = self._create_button_object(master=self.gui, text='', command=selection_callback(idx),
                                                 anchor=W, fontsize=10)
                self.key_id_to_widget[key.key_id] = obj  # add to key_id -> widget dict
                self.key_id_to_key_object[key.key_id] = key  # add to key_id -> Key dict

            else:
                raise ValueError('Key type: {} not handled yet in build_display method'.format(key.type))

            obj.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)
            self.key_id_to_widget[key.key_id] = obj  # add to key_id -> widget dict
            self.key_id_to_key_object[key.key_id] = key  # add to key_id -> Key dict

    def start_display(self):
        """ Start display"""
        # start eye gaze server then run mainloop
        c_file_path = os.path.join(ROOT_DIR, 'lib', 'Interaction_Streams_101.exe')
        self.gaze_server_process = subprocess.Popen(c_file_path)
        self.gui.mainloop()

    def predict_on_trace(self):
        """ run prediction on trace currently held in buffer and add predicted text to the displayed text"""
        mouse_trace = self.mouse_trace_buffer.copy()
        mouse_trace.reverse()  # to put list in chronological order

        possible_words = self.trace_model.predict(mouse_trace, beam_width=self.beam_width)
        if not possible_words:
            print('Trace model returned no possible words - try again')
            return False

        possible_words = possible_words[:self.beam_width]
        print('top {} possible words are: {}'.format(self.beam_width, possible_words))

        # Capitalize first word in new sentence
        current_phrases = self._get_current_display_phrases()
        if current_phrases[0] == "" or current_phrases[0][-1] in ['.', '!', '?']:
            possible_words = [word.capitalize() for word in possible_words]

        # Use language model to predict new top phrase
        new_top_phrases = self.language_model.get_new_top_phrases(possible_words)

        self._set_display_phrases(new_top_phrases)

    def pick_from_prediction_list(self, idx_of_selected_phrase):
        """ Callback for each of the displayed option buttons
        when one is selected we set that phrase to be THE only top phrase
        """
        current_phrases = self._get_current_display_phrases()
        selected_phrase = current_phrases[idx_of_selected_phrase]
        self._set_display_phrases([selected_phrase] + ['']*(self.beam_width-1))
        self.language_model.set_top_phrases([selected_phrase])

    def show_top_pred_word_popup(self, current_key_in_focus):
        """
        Show a popup over the current key in focus displaying the top predicted new word.
        This will allow the user to see whether the top prediction is what they intended without repeatedly having
        to check the display frame.
        This function is called from within on_single_key_in_focus_for_required_time()
        Parameters
        ----------
        current_key_in_focus: str
            key_id of the key that was in focus at the end of the trace
        """
        key_obj = self.key_id_to_key_object[current_key_in_focus]
        current_phrases = self._get_current_display_phrases()
        top_phrase = current_phrases[0]

        if ' ' in top_phrase:
            top_phrase_words = top_phrase.split()
            latest_word = top_phrase_words[-1]
        else:
            latest_word = top_phrase

        label = Label(self.gui, text=latest_word, fg='red', bg=rgb_to_hex(self.initial_bg),
                      activebackground=rgb_to_hex(self.initial_bg), font=("Calibri 20 bold"))
        label.place(relx=key_obj.x1, rely=key_obj.y1, relwidth=key_obj.w, relheight=key_obj.h)
        time.sleep(0.3)
        label.destroy()

    def press_speak(self):
        top_phrase_widget = self.key_id_to_widget['display_box_0']
        top_phase = top_phrase_widget.cget('text')
        TextToSpeech().speak_text_in_new_thread(text=top_phase)

    def press_delete(self):
        current_phrases = [phrase for phrase in self._get_current_display_phrases() if phrase != '']
        updated_phrases = []
        for current_phrase in current_phrases:
            words = current_phrase.split(' ')
            new_words = words[:-1]
            updated_phrases.append(' '.join(new_words))
        updated_phrases = list(set(updated_phrases))  # remove duplicates

        self._set_display_phrases(updated_phrases)
        self.language_model.set_top_phrases(updated_phrases)

    def clear_display(self):
        """ clear display text and trace buffer"""

        for idx in range(self.beam_width):
            display_widget = self.key_id_to_widget['display_box_{}'.format(idx)]
            display_widget.configure(text='')

        self.clear_trace_buffer()
        self.language_model.reset()

    def _set_display_phrases(self, phrases):
        assert len(phrases) <= self.beam_width
        for idx in range(self.beam_width):
            widget = self.key_id_to_widget['display_box_{}'.format(idx)]
            if idx < len(phrases):
                phrase = phrases[idx]
            else:
                phrase = ''
            if len(phrase) > 44:
                widget.configure(anchor=E)  # align text right after reached end of line so latest words can be read
            else:
                widget.configure(anchor=W)
            widget.configure(text=phrase)

    def _get_current_display_phrases(self):
        phrases = []
        for idx in range(self.beam_width):
            widget = self.key_id_to_widget['display_box_{}'.format(idx)]
            phrases.append(widget.cget('text'))
        return phrases

    def clear_trace_buffer(self):
        self.mouse_trace_buffer.clear()

    def exit(self):
        self.key_timer.cancel()
        self.gui.destroy()
        self.gaze_server_process.kill()

    def change_key_in_focus(self, new_key_in_focus):
        """
        Update the self.current_key_in_focus attribute with the key_id of the new key in focus.
        This method is called by
        Parameters
        ----------
        new_key_in_focus: str
            key_id of the new key in focus
        """
        self.key_timer.cancel()

        current_key_in_focus = self.current_key_in_focus
        # Reset the colour to default as we have left that key now
        if current_key_in_focus is not None:
            current_widget = self.key_id_to_widget.get(current_key_in_focus)
            current_widget.configure(bg=rgb_to_hex(self.initial_bg), activebackground=rgb_to_hex(self.initial_bg))

        # If statement prevents timer restarting on same key after word is predicted
        print('Current key in focus is {} - New key in focus is {}'.format(current_key_in_focus, new_key_in_focus))
        self.current_key_in_focus = new_key_in_focus

        self.key_timer.restart()

    def on_single_key_in_focus_for_required_time(self):

        self.key_timer.cancel()

        current_key_in_focus = self.current_key_in_focus  # define here in case it changes during processing

        if current_key_in_focus is None:
            self.key_timer.restart()
            return

        widget_in_focus = self.key_id_to_widget[current_key_in_focus]
        new_hex = rgb_to_hex(self.initial_bg)
        widget_in_focus.configure(bg=new_hex, activebackground=new_hex)

        key_object_in_focus = self.key_id_to_key_object[current_key_in_focus]

        # If mouse trace is currently being recorded then stop the trace, predict the intended word and then clear the trace
        if self.record_eye_trace:
            self.record_eye_trace = False
            SFX().button_click_sfx_in_new_thread(type='unselect')  # play button unselect sound in new thread
            if self.mouse_trace_buffer:
                self.change_border_colour(colour='black')
                if key_object_in_focus.type == 'text_key':
                    self.predict_on_trace()  # this function calls the prediction
                    self.show_top_pred_word_popup(current_key_in_focus)
                self.clear_trace_buffer()  # clear trace ready for next swype

        else:  # mouse trace is NOT currently being recorded
            SFX().button_click_sfx_in_new_thread(type='select')  # play button unselect sound in new thread

            # If key in focus is a non-text key then we execute that buttons command but do NOT start trace recorded
            if key_object_in_focus.type in ['speak_button', 'delete_button', 'clear_button', 'exit_button', 'display_frame']:
                widget_in_focus.invoke()  # trigger click on this button

            elif key_object_in_focus.type == 'punctuation_key':
                punctuation = key_object_in_focus.contents[0]
                self.language_model.manually_add_word(word=punctuation, sep='')
                updated_phrases = self.language_model.get_current_top_phrases()
                self._set_display_phrases(updated_phrases)

            elif key_object_in_focus.type == 'text_key':
                self.record_eye_trace = True
                self.change_border_colour(colour='red')
                print('Turning ON mouse recording')
            elif key_object_in_focus.type == 'null_key':
                pass
            else:
                raise ValueError('Unknown key type')

        self.key_timer.restart()

    def change_border_colour(self, colour='red'):
        """ Change border colour"""
        for widget in self.key_id_to_widget.values():
            widget.configure(highlightbackground=colour)
        self.gui.update()

    def on_every_interval_a_key_is_in_focus(self):
        """
        At every interval that a key is in focus we do the following things

        1) get the current eye position
        2) Add the latest eye coordinate to the trace buffer IF the trace is currently being recorded
        3) if there are any keys in focus
            - if the key in focus hasn't changed
                - if the key has been in focus for required time call on_single_key_in_focus_for_required_time
                - else darked the colour of the key and increment duration_in_focus
            - elif the key in focus has changed call change_key_in_focus()
           else if there are no keys in focus then call gaze_has_left_window()
        """

        # get current eye position relative to window
        try:
            relx, rely = self.get_eye_coords_relative_to_window()
        except NoGazeDataReturned:
            self.gaze_has_left_window()
            return

        # Add current eye position to buffer if trace recording is currently ON
        if self.record_eye_trace:
            self.add_current_eye_position_to_buffer(relx, rely)

        # get a list containing the key_ids of the current key(s) in focus
        # multiple keys can be in focus if gaze is exactly on border
        keys_in_focus = self.keyboard.get_key_ids_at_point(x=relx, y=rely)

        if keys_in_focus:

            if self.current_key_in_focus in keys_in_focus:
                # if key in focus hasn't changed then darken the current key in focus
                widget_in_focus = self.key_id_to_widget.get(self.current_key_in_focus)

                # FIXME line below is a hack to account for the fact that the main timer finished before the periodic
                # FIXME .. has time to send it's final callback
                # darken colour of current key in focus
                current_hex = widget_in_focus.cget('bg')
                new_hex = rgb_to_hex(tuple(np.array(hex_to_rgb(current_hex)) + np.array(self.rgb_increment)))
                widget_in_focus.configure(bg=new_hex, activebackground=new_hex)

            else:
                self.change_key_in_focus(new_key_in_focus=keys_in_focus[0])

        else:
            self.gaze_has_left_window()  # resets colour of last key in focus and sets current_key_in_focus to None

    def add_current_eye_position_to_buffer(self, relx, rely):
        """
        Add the current gaze position to the trace buffer

        Parameters
        ---------
        relx: float
            current x coords relative to window - e.g. relx=0.5 means gaze is 50% across window horizontally
        rely: float
        """

        # append coordinate to buffer only if euclidean distance exceeds minimum delta
        if not self.mouse_trace_buffer:
            self.mouse_trace_buffer.appendleft((relx, rely))  # if buffer is empty add first point
        else:
            prev_coords = self.mouse_trace_buffer[0]
            euclidean_dist = np.linalg.norm(np.array((relx, rely) - np.array((prev_coords))))
            if euclidean_dist > 0.05 or not self.mouse_trace_buffer:
                self.mouse_trace_buffer.appendleft((relx, rely))

    def get_eye_coords_relative_to_window(self):
        """
        Get x, y coords of eye position relative to the window
        Returns
        -------
        relx: float
        rely: float
        """
        screen_relx, screen_rely = get_eye_coords_relative_to_screen()

        # Get coords relative to window
        relx = (screen_relx * self.gui.winfo_screenwidth() - self.gui.winfo_x()) / self.gui.winfo_width()
        rely = (screen_rely * self.gui.winfo_height() - self.gui.winfo_y()) / self.gui.winfo_height()

        return relx, rely

    def gaze_has_left_window(self):
        """ Called by on_every_interval_a_key_is_in_focus() if there are no keys in focus

        - resets the colour of the last key in the focus and then sets the current_key_in_focus=None
        """

        widget_in_focus = self.key_id_to_widget.get(self.current_key_in_focus)

        if widget_in_focus:
            new_hex = rgb_to_hex(self.initial_bg)
            widget_in_focus.configure(bg=new_hex, activebackground=new_hex)

        self.current_key_in_focus = None

    def set_trace_model(self, model):
        """
        Set prediction model - carry out some checks on the model
        Parameters
        ----------
        model: nuvox.trace_model.TraceModel
        """

        # TODO will need some way of checking that the models keyboard is the same as the one set for display

        if not isinstance(model, nuvox.trace_model.TraceModel):
            raise ValueError('Parameter: model must be an instance of nuvox.trace_model.TraceModel')

        if model.config is None:
            raise (ValueError('model config must be set before predictions can be made'))

        self.trace_model = model

    def set_language_model(self, model):
        """
        Set prediction model - carry out some checks on the model
        Parameters
        ----------
        model: nuvox.language_model.GPT2
        """

        if not isinstance(model, nuvox.language_model.GPT2):
            raise ValueError('Parameter: model must be an instance of nuvox.trace_model.TraceModel')

        self.language_model = model
        self.language_model.beam_width = self.beam_width

    def _create_button_object(self, master, text=None, command=None, anchor=CENTER, fontsize=18):
        """
        Create and return TKinter Button object
        Parameters
        ----------
        master:
        text: str
        command: function

        Returns
        -------
        button: tkinter.Button
        """
        button = Button(master=master,
                        text=text,
                        command=command,
                        fg=rgb_to_hex(self.default_fg),
                        bg=rgb_to_hex(self.initial_bg),
                        activebackground=rgb_to_hex(self.initial_bg),
                        highlightthickness=2,
                        highlightbackground='black',
                        relief=RAISED,
                        anchor=anchor,
                        font=("Calibri {}".format(fontsize)))
        return button


def rgb_to_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """

    return "#%02x%02x%02x" % rgb


def hex_to_rgb(hex):
    """ Converts hex string to rgb tuple"""
    h = hex.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

if __name__ == "__main__":
    """ Testing"""
    from nuvox.config.keyboard_config import nuvox_standard_keyboard, nuvox_standard_keyboard_2
    from nuvox.keyboard import Keyboard

    _keyboard = Keyboard()
    _keyboard.build_keyboard(nuvox_standard_keyboard_2)

    _trace_model = TraceModel()
    _trace_model.load_model(model_dir=os.path.join(ROOT_DIR, 'models', 'trace_models', '11_01_2020_16_57_43'))

    _language_model = GPT2()
    _language_model.load_model()  # by default the model will be loaded using the model name

    _display = Display(_keyboard, display_width=450, display_height=600)
    _display.set_trace_model(_trace_model)
    _display.set_language_model(_language_model)
    _display.start_display()


