from collections import deque
import time

from tkinter import *

import numpy as np

import nuvox
from nuvox.trace_model import TraceModel
from nuvox.language_model import GPT2
from nuvox.utils.text_to_speech import TextToSpeech
from nuvox.utils.sound_effects import SFX
from nuvox.timer_thread import MyTimer

from nuvox.multiple_choice_test import OptionDialog


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

        self.beam_width = 5

        self.language_model = GPT2()
        self.language_model.beam_width = self.beam_width

        self.gui = Tk()
        self.gui.configure(background="steel blue")
        self.gui.title("nuvox keyboard")
        self.gui.geometry("{}x{}".format(self.display_width, self.display_height))
        self.gui.resizable(width=False, height=False)
        self.gui.bind('<Leave>', func=self.mouse_has_left_window)

        # For swype controls
        self.gui.bind('<Motion>', self.record_mouse_position)
        self.current_key_in_focus = None  # track the id of the key currently in focus
        self.required_time_in_focus = 1  # number of ms a key has to be hovered on before record_mouse_trace is toggled
        self.interval_secs = 0.1
        self.timer = MyTimer(self.required_time_in_focus, self.interval_secs,
                             self.on_single_key_in_focus_for_required_time,
                             self.on_every_second_a_key_is_in_focus)
        self.record_mouse_trace = False  # Flag to keep track of whether mouse movements should be recorded currently

        # Controlling colours of keys
        self.default_fg = (255, 255, 255)
        self.initial_bg = (32, 32, 32)
        self.final_bg = (64, 0, 0)
        number_colour_increments = int(self.required_time_in_focus / self.interval_secs)
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

            if key.type == 'button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), highlightthickness=2, highlightbackground='black',
                             relief=RAISED, font=("Calibri 18"))

            elif key.type == 'speak_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), highlightthickness=2, highlightbackground='black', relief=RAISED,
                             command=lambda: self.press_speak(), font=("Calibri 10"))

            elif key.type == 'delete_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), highlightthickness=2, highlightbackground='black', relief=RAISED,
                             command=lambda: self.press_delete(), font=("Calibri 10"))

            elif key.type == 'clear_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), highlightthickness=2, highlightbackground='black', relief=RAISED,
                             command=lambda: self.clear_display(), font=("Calibri 10"))

            elif key.type == 'exit_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), highlightthickness=2, highlightbackground='black', relief=RAISED,
                             command=lambda: self.exit(), font=("Calibri 10"))

            elif key.type == 'display_frame':
                display_frame = Frame(self.gui)
                display_frame.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)
                for idx in range(self.beam_width):
                    selection_callback = lambda idx: lambda: self.pick_from_prediction_list(idx)
                    obj = Button(display_frame, text=''.format(idx), font=("Calibri 10"), anchor=W,
                                 command=selection_callback(idx),
                                 fg=rgb_to_hex(self.default_fg),
                                 bg=rgb_to_hex(self.initial_bg),
                                 activebackground=rgb_to_hex(self.initial_bg),
                                 highlightthickness=2, highlightbackground='black', relief=RAISED
                                 )
                    obj.place(relx=0, rely=(idx / self.beam_width), relwidth=1, relheight=(1 / self.beam_width))
                    obj.bind('<Enter>', self.change_key_in_focus)
                    key_id = 'display_button_{}'.format(idx)
                    self.key_id_to_widget[key_id] = obj  # add to key_id -> widget dict
                    self.key_id_to_key_object[key_id] = key  # add to key_id -> Key dict
                continue

            else:
                raise ValueError('Key type: {} not handled yet in build_display method'.format(key.type))

            obj.bind('<Enter>', self.change_key_in_focus)

            obj.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)

            self.key_id_to_widget[key.key_id] = obj  # add to key_id -> widget dict
            self.key_id_to_key_object[key.key_id] = key  # add to key_id -> Key dict

    def start_display(self):
        """ Start display"""
        self.gui.mainloop()

    def predict_on_trace(self):
        """ run prediction on trace currently held in buffer and add predicted text to the displayed text"""
        mouse_trace = self.mouse_trace_buffer.copy()
        mouse_trace.reverse()  # to put list in chronological order

        possible_words = self.trace_model.predict(mouse_trace, beam_width=self.beam_width)
        if not possible_words:
            print('Trace model returned no possible words - try again')
            return False

        possible_words = possible_words[:self.beam_width]  # TODO currently just limiting the number of words that the language model can predict on
        print('top 10 possible words are: ', possible_words)

        # Capitalize first word in new sentence TODO should also check if last char is . or ? or !
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
                      activebackground=rgb_to_hex(self.initial_bg), font=("Calibri 16 bold"))
        label.place(relx=key_obj.x1, rely=key_obj.y1, relwidth=key_obj.w, relheight=key_obj.h)
        time.sleep(0.3)
        label.destroy()


    def press_speak(self):
        top_phrase_widget = self.key_id_to_widget['display_button_0']
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
            display_widget = self.key_id_to_widget['display_button_{}'.format(idx)]
            display_widget.configure(text='')

        self.clear_trace_buffer()
        self.language_model.reset()

    def _set_display_phrases(self, phrases):
        assert len(phrases) <= self.beam_width
        for idx in range(self.beam_width):
            widget = self.key_id_to_widget['display_button_{}'.format(idx)]
            if idx < len(phrases):
                phrase = phrases[idx]
            else:
                phrase = ''
            if len(phrase) > 44:
                widget.configure(anchor=E)  # align text right after reached end of line so latest words can be read
            widget.configure(text=phrase)

    def _get_current_display_phrases(self):
        phrases = []
        for idx in range(self.beam_width):
            widget = self.key_id_to_widget['display_button_{}'.format(idx)]
            phrases.append(widget.cget('text'))
        return phrases

    def clear_trace_buffer(self):
        self.mouse_trace_buffer.clear()

    def exit(self):
        self.timer.cancel()
        self.gui.destroy()

    def change_key_in_focus(self, event):
        """
        Called by the Enter event on the main keys - updates the self.key_in_focus attribute to be the key in focus
        """

        current_key_in_focus = self.current_key_in_focus

        # Reset the colour to default as we have left that key now
        if current_key_in_focus is not None:
            current_widget = self.key_id_to_widget[current_key_in_focus]
            current_widget.configure(bg=rgb_to_hex(self.initial_bg), activebackground=rgb_to_hex(self.initial_bg))

        widget_in_focus = event.widget
        widget_to_key_id = {v: k for k, v in self.key_id_to_widget.items()}  # TODO probably shouldn't have to do this every time
        new_key_in_focus = widget_to_key_id[widget_in_focus]

        # If statement prevents timer restarting on same key after word is predicted
        if new_key_in_focus != current_key_in_focus and new_key_in_focus is not None:
            print('Current key in focus is {} - New key in focus is {}'.format(current_key_in_focus, new_key_in_focus))
            self.timer.cancel()
            self.timer = MyTimer(self.required_time_in_focus, self.interval_secs,
                                 self.on_single_key_in_focus_for_required_time,
                                 self.on_every_second_a_key_is_in_focus)
            self.timer.start()

            self.current_key_in_focus = new_key_in_focus

    def on_single_key_in_focus_for_required_time(self):

        current_key_in_focus = self.current_key_in_focus  # define here in case it changes

        # If mouse trace is currently being recorded then stop the trace, predict the intended word and then clear the trace
        if self.record_mouse_trace:
            SFX().button_click_sfx_in_new_thread(type='unselect')  # play button unselect sound in new thread
            if self.mouse_trace_buffer:
                self.change_border_colour(colour='black')
                self.predict_on_trace()  # this function calls the prediction
                self.show_top_pred_word_popup(current_key_in_focus)
                self.clear_trace_buffer()  # clear trace ready for next swype
                self.record_mouse_trace = False
                print('Turing OFF mouse recording')

        else:  # mouse trace is NOT currently being recorded
            SFX().button_click_sfx_in_new_thread(type='select')  # play button unselect sound in new thread

            key_object_in_focus = self.key_id_to_key_object[current_key_in_focus]

            # If key in focus is a non-text key then we execute that buttons command but do NOT start trace recorded
            if key_object_in_focus.type in ['speak_button', 'delete_button', 'clear_button', 'exit_button', 'display_frame']:
                widget_in_focus = self.key_id_to_widget[current_key_in_focus]
                widget_in_focus.invoke()  # trigger click on this button
            else:
                self.record_mouse_trace = True
                self.change_border_colour(colour='red')
                print('Turning ON mouse recording')

    def change_border_colour(self, colour='red'):
        """ Change border colour"""
        for widget in self.key_id_to_widget.values():
            widget.configure(highlightbackground=colour)
        self.gui.update()

    def on_every_second_a_key_is_in_focus(self, seconds_passed):

        # Change colour value of key in focus
        if self.current_key_in_focus is not None:
            widget_in_focus = self.key_id_to_widget[self.current_key_in_focus]
            # FIXME line below is a hack to account for the fact that the main timer finished before the periodic
            # FIXME .. has time to send it's final callback
            if seconds_passed >= self.required_time_in_focus - self.interval_secs - 1e-3:
                new_hex = rgb_to_hex(self.initial_bg)
            else:
                current_hex = widget_in_focus.cget('bg')
                new_hex = rgb_to_hex(tuple(np.array(hex_to_rgb(current_hex)) + np.array(self.rgb_increment)))
            widget_in_focus.configure(bg=new_hex, activebackground=new_hex)
            print('{} seconds passed'.format(seconds_passed))

    def record_mouse_position(self, event):
        """Record mouse trace when flag is set to True"""

        if self.record_mouse_trace:

            relx = (self.gui.winfo_pointerx() - self.gui.winfo_x()) / self.gui.winfo_width()
            rely = (self.gui.winfo_pointery() - self.gui.winfo_y()) / self.gui.winfo_height()

            # append coordinate to buffer only if euclidean distance exceeds minimum delta
            if not self.mouse_trace_buffer:
                self.mouse_trace_buffer.appendleft((relx, rely))
            else:
                prev_coords = self.mouse_trace_buffer[0]
                euclidean_dist = np.linalg.norm(np.array((relx, rely) - np.array((prev_coords))))
                if euclidean_dist > 0.05 or not self.mouse_trace_buffer:
                    self.mouse_trace_buffer.appendleft((relx, rely))

                    #self.plot_single_trace_point(relx, rely)

                    print('x={:.2f}, y={:.2f}'.format(relx, rely))

    def mouse_has_left_window(self, event):
        """ Called from record_mouse_position() when x, y coords are found to fall outside window
        it cancels the timer, resets the colour of the last key in focus and then sets the current key in focus to None
        """
        self.timer.cancel()
        print('mouse has left window')
        widget_in_focus = self.key_id_to_widget[self.current_key_in_focus]
        new_hex = rgb_to_hex(self.initial_bg)
        widget_in_focus.configure(bg=new_hex, activebackground=new_hex)


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

        print('Available vocab words are: \n\n {}'.format(self.trace_model.config.VOCAB))

    def plot_trace(self, trace):
        """ plot trace
        Parameters
        ----------
        trace: list(tuple)
            list of relative (x, y) coords to plot
        """

        rgb_cols = [(255, yellow, 0) for yellow in np.linspace(255, 0, len(trace), dtype=int)]
        hex_cols = [rgb_to_hex(rgb) for rgb in rgb_cols]

        # Plot trace with yellow->red heatmap
        for idx, (x, y) in enumerate(trace):
            self.plot_single_trace_point(x, y, hex_cols[idx])

    def plot_single_trace_point(self, x, y, colour='red'):
        """
        Plot single point of trace
        Parameters
        ----------
        x: float
        y: float
        colour: str
            colour name of hex string
        """

        if (0 <= x <= 1) and (0 <= y <= 1):
            obj = Label(self.gui, text='', bg=colour)  # all same colour for now
            obj.place(relx=x, rely=y, width=10, height=10)
            self.trace_labels.append(obj)
            self.gui.update()


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
    from nuvox.config.keyboard_config import nuvox_standard_keyboard, nuvox_qwerty_keyboard
    from nuvox.keyboard import Keyboard

    _keyboard = Keyboard()
    _keyboard.build_keyboard(nuvox_standard_keyboard)

    _model = TraceModel()
    _model.load_model('/home/luka/PycharmProjects/nuvox/models/trace_models/11_01_2020_16_57_43')

    _display = Display(_keyboard, display_width=900, display_height=1200)
    _display.set_trace_model(_model)
    _display.start_display()


