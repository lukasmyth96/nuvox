from collections import deque
import random
import asyncio
import threading
import time
import queue
from tkinter import *

import numpy as np

import nuvox
from nuvox.trace_model import TraceModel
from nuvox.language_model import GPT2
from nuvox.utils.text_to_speech import speak_text
from nuvox.utils.common import add_line_breaks, strip_new_lines
from nuvox.timer_thread import MyTimer


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

        # TODO build new want of selecting keys with hover:
        self.current_key_in_focus = None  # track the id of the key currently in focus
        self.required_time_in_focus = 2  # number of ms a key has to be hovered on before record_mouse_trace is toggled
        self.interval_secs = 0.2
        self.timer = MyTimer(self.required_time_in_focus, self.interval_secs,
                             self.on_single_key_in_focus_for_required_time,
                             self.on_every_second_a_key_is_in_focus)
        self.record_mouse_trace = False  # Flag to keep track of whether mouse movements should be recorded currently

        # Controlling colours of keys
        self.default_fg = (0, 0, 0)
        self.initial_bg = (0, 255, 255)
        self.final_bg = (0, 64, 255)
        number_colour_increments = int(self.required_time_in_focus / self.interval_secs)
        self.rgb_increment = tuple([int(val) for val in ((np.array(self.final_bg) - np.array(self.initial_bg)) / number_colour_increments)])

        self.left_mouse_down = False
        self.gui.bind('<Motion>', self.record_mouse_position)

        self.display_variable = StringVar()

        # dict mapping key_id to TK object
        self.key_id_to_widget = {}

        self.mouse_trace_buffer = deque(maxlen=200)  # store coordinates of mouse in buffer of fixed length
        self.trace_labels = []  # store label objects for trace
        self.build_display()

    def build_display(self):
        """ Build gui from information in keyboard object"""
        for key in self.keyboard.keys:

            if key.type == 'button':
                text = ' '.join(key.contents).upper()
                click_callback = lambda id: lambda: self.press_key(id)
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), command=click_callback(key.key_id), font=("Calibri 18"))

            elif key.type == 'speak_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), command=lambda: self.press_speak(), font=("Calibri 10"))

            elif key.type == 'delete_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), command=lambda: self.press_delete(), font=("Calibri 10"))

            elif key.type == 'clear_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), command=lambda: self.clear_display(), font=("Calibri 10"))

            elif key.type == 'exit_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg=rgb_to_hex(self.default_fg), bg=rgb_to_hex(self.initial_bg),
                             activebackground=rgb_to_hex(self.initial_bg), command=lambda: self.exit(), font=("Calibri 10"))

            elif key.type == 'display':
                obj = Label(self.gui, textvariable=self.display_variable, justify=LEFT, anchor=NW, font=("Calibri 12"))

            else:
                raise ValueError('Key type: {} not handled yet in build_display method'.format(key.type))

            obj.bind('<Enter>', self.change_key_in_focus)

            obj.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)
            self.key_id_to_widget[key.key_id] = obj

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

        possible_words = possible_words[:self.beam_width]  # TODO currently just limiting the numbere of words that the language model can predict on
        print('top 10 possible words are: ', possible_words)

        # Capitalize first word in new sentence TODO should also check if last char is . or ? or !
        current_text = self._get_display_text()
        if current_text == "" or current_text[-1] in ['.', '!', '?']:
            possible_words = [word.capitalize() for word in possible_words]

        # Use language model to predict new top phrase
        new_top_phrase = self.language_model.get_new_top_phrase(possible_words)

        self._set_display_text(new_top_phrase)

    def press_key(self, key_id):
        """ method for updating display text when key is pressed"""

        key_contents = self.keyboard.key_id_to_contents[key_id]
        if len(key_contents) == 1:
            text_to_add = key_contents[0]
        else:
            if 'i' in key_contents:
                text_to_add = ' I'
            elif 'a' in key_contents:
                if self._get_display_text() == '':
                    text_to_add = ' A'
                else:
                    text_to_add = ' a'
            else:
                return

        self.language_model.manually_add_text(text_to_add)
        self._set_display_text(self.language_model.get_current_top_phrase())

    def press_speak(self):
        """
        Speak text on display
        """
        display_text = self.display_variable.get()
        display_text.lstrip('. ')
        speak_text(text=display_text)

    def press_delete(self):
        """
        Delete last word on display
        """
        current_display_text = self._get_display_text()
        words = current_display_text.split(' ')
        new_words = words[:-1]
        new_display_text = ' '.join(new_words)
        self._set_display_text(new_display_text)

        self.language_model.delete_last_word()

    def clear_display(self):
        """ clear display text and trace buffer"""
        self._set_display_text("")
        self.clear_trace()
        self.language_model.reset()

    def clear_trace(self):
        """ Clear only the trace buffer """
        # destroy all labels and clear trace buffer
        for label in self.trace_labels:
            label.destroy()

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

        # FIXME - the following will not work in debug if the mouse moves at all
        relx = (self.gui.winfo_pointerx() - self.gui.winfo_x()) / self.gui.winfo_width()
        rely = (self.gui.winfo_pointery() - self.gui.winfo_y()) / self.gui.winfo_height()
        keys_in_focus = self.keyboard.get_key_ids_at_point(relx, rely)

        if not keys_in_focus:
            new_key_in_focus = None
        elif len(keys_in_focus) == 1:
            new_key_in_focus = keys_in_focus[0]
        elif len(keys_in_focus) == 2:
            keys_in_focus.remove(current_key_in_focus)  # happens when mouse position is right on border of two keys
            new_key_in_focus = keys_in_focus[0]
        else:
            raise Exception('Found three keys at position ({:.1f}, {:.1f})'.format(relx, rely))

        print('New key in focus is {} - restarting timer'.format(new_key_in_focus))

        self.timer.cancel()
        self.timer = MyTimer(self.required_time_in_focus, self.interval_secs,
                             self.on_single_key_in_focus_for_required_time,
                             self.on_every_second_a_key_is_in_focus)
        self.timer.start()

        self.current_key_in_focus = new_key_in_focus

    def on_single_key_in_focus_for_required_time(self):
        print('record_mouse_trace changing from {}'.format(self.record_mouse_trace))
        if self.record_mouse_trace:
            if self.mouse_trace_buffer:
                self.predict_on_trace()  # this function calls the prediction
                self.clear_trace()  # clear trace ready for next word

        self.record_mouse_trace = not self.record_mouse_trace

    def on_every_second_a_key_is_in_focus(self, seconds_passed):

        # Change colour value of key in focus
        widget_in_focus = self.key_id_to_widget[self.current_key_in_focus]
        if seconds_passed == self.required_time_in_focus:
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

                    self.plot_single_point(relx, rely)

                    print('x={:.2f}, y={:.2f}'.format(relx, rely))

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
            self.plot_single_point(x, y, hex_cols[idx])

    def plot_single_point(self, x, y, colour='red'):
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

    def _get_display_text(self):
        """ Get display text but remove new line chars"""
        return strip_new_lines(self.display_variable.get())

    def _set_display_text(self, text):
        """ Set display text but insert line breaks """
        # TODO need to find a beetter way to determine when the line is full
        self.display_variable.set(add_line_breaks(text=text, char_lim=44))


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


