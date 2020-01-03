from collections import deque
import random
import time
from tkinter import *

import numpy as np

import nuvox
from nuvox.model import NuvoxModel
from nuvox.traces import get_random_trace


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

        self.prediction_model = None

        self.gui = Tk()
        self.gui.configure(background="light green")
        self.gui.title("nuvox keyboard")
        self.gui.geometry("{}x{}".format(self.display_width, self.display_height))
        self.gui.resizable(width=False, height=False)

        self.left_mouse_down = False
        self.gui.bind('<Motion>', self.record_mouse_position)
        self.gui.bind('<Button-1>', self.b1_down)
        self.gui.bind('<ButtonRelease-1>', self.release_b1)

        self.display_variable = StringVar()

        # dict mapping key_id to TK object
        self.key_list = []

        self.mouse_trace_buffer = deque(maxlen=200)  # store coordinates of mouse in buffer of fixed length
        self.trace_labels = []  # store label objects for trace
        self.build_display()

    def build_display(self):
        """ Build gui from information in keyboard object"""
        for key in self.keyboard.keys:

            if key.type == 'button':
                text = ' '.join(key.contents).upper()
                callback = lambda id: lambda: self.press_key(id)
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=callback(key.key_id), font=("Calibri 18"))

            elif key.type == 'enter_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.press_enter(), font=("Calibri 10"))

            elif key.type == 'clear_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.clear_display(), font=("Calibri 10"))

            elif key.type == 'exit_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.exit(), font=("Calibri 10"))

            elif key.type == 'display':
                obj = Entry(self.gui, textvariable=self.display_variable, font=("Calibri 18"))

            else:
                raise ValueError('Key type: {} not handled yet in build_display method'.format(key.type))

            obj.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)
            self.key_list.append(obj)

    def start_display(self):
        """ Start display"""
        self.gui.mainloop()

    def predict_on_trace(self):
        """ run prediction on trace currently held in buffer and add predicted text to the displayed text"""
        mouse_trace = self.mouse_trace_buffer.copy()
        mouse_trace.reverse()  # to put list in chronological order
        predicted_word = self.prediction_model.predict(mouse_trace)

        current_display_text = self.display_variable.get()
        new_display_text = ' '.join([current_display_text, predicted_word])
        self.display_variable.set(new_display_text)

    def press_key(self, key_id):
        """ method for updating display text when key is pressed"""

        # TODO currently just selects character randomly from the keys contents

        key_contents = self.keyboard.key_id_to_contents[key_id]
        random_choice = random.choice(key_contents)

        current_display_text = self.display_variable.get()
        # new_display_text = current_display_text + str(random_choice)
        #
        # self.display_variable.set(new_display_text)

    def press_enter(self):
        """
        Get and plot a random trace for the currently displayed text

        """

        displayed_text = self.display_variable.get()
        if displayed_text:

            random_trace = get_random_trace(self.keyboard, displayed_text, add_gradients=False)
            self.plot_trace(trace=random_trace)

    def clear_display(self):
        """ clear display text and trace buffer"""
        self.display_variable.set("")
        self.clear_trace()

    def clear_trace(self):
        """ Clear only the trace buffer """
        # destroy all labels and clear trace buffer
        for label in self.trace_labels:
            label.destroy()

        self.mouse_trace_buffer.clear()

    def exit(self):
        self.gui.destroy()

    def b1_down(self, event):
        """press down left mouse button"""
        self.left_mouse_down = True

    def release_b1(self, event):
        """ release left click"""
        self.left_mouse_down = False

        # Automatically predict on trace and then call clear to reset buffer
        if self.mouse_trace_buffer:
            self.predict_on_trace()  # this function calls the prediction
            self.clear_trace()  # clear trace ready for next work

    def record_mouse_position(self, event):
        """record mouse movement when left mouse button is held down"""
        if self.left_mouse_down:
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

    def set_prediction_model(self, model):
        """
        Set prediction model - carry out some checks on the model
        Parameters
        ----------
        model: nuvox.model.NuvoxModel
        """

        # TODO will need some way of checking that the models keyboard is the same as the one set for display

        if not isinstance(model, nuvox.model.NuvoxModel):
            raise ValueError('Parameter: model must be an instance of nuvox.model.NuvoxModel')

        if model.config is None:
            raise (ValueError('model config must be set before predictions can be made'))

        self.prediction_model = model

        print('Available vocab words are: \n\n {}'.format(self.prediction_model.config.VOCAB))

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

        assert 0 <= x <= 1
        assert 0 <= y <= 1
        obj = Label(self.gui, text='', bg=colour)  # all same colour for now
        obj.place(relx=x, rely=y, relwidth=0.01, relheight=0.01)
        self.trace_labels.append(obj)
        self.gui.update()


def rgb_to_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


if __name__ == "__main__":
    """ Testing"""
    from nuvox.config.keyboard_config import nuvox_standard_keyboard
    from nuvox.keyboard import Keyboard

    _keyboard = Keyboard()
    _keyboard.build_keyboard(nuvox_standard_keyboard)

    _model = NuvoxModel()
    _model.load_model('../models/02_01_2020_17_30_42_top2500_078acc')

    _display = Display(_keyboard, display_width=900, display_height=1200)
    _display.set_prediction_model(_model)
    _display.start_display()


