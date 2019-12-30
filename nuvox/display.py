from collections import deque
import random
import time
from tkinter import *

import numpy as np


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

        self.gui = Tk()
        self.gui.configure(background="light green")
        self.gui.title("nuvox keyboard")
        self.gui.geometry("{}x{}".format(self.display_width, self.display_height))
        self.gui.resizable(width=False, height=False)
        self.gui.bind('<Motion>', self.record_mouse_position)

        self.display_text = ""
        self.display_variable = StringVar()

        # dict mapping key_id to TK object
        self.key_list = []

        self.trace_buffer = deque(maxlen=200)  # store coordinates of mouse in buffer of fixed length
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
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.plot_trace(), font=("Calibri 10"))

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

    def press_key(self, key_id):
        """ method for updating display text when key is pressed"""

        # TODO currently just selects character randomly from the keys contents

        key_contents = self.keyboard.key_id_to_contents[key_id]
        random_choice = random.choice(key_contents)

        self.display_text = self.display_text + str(random_choice)

        self.display_variable.set(self.display_text)

    # of text entry box
    def clear_display(self):
        self.display_text = ""
        self.display_variable.set("")

        # destroy all labels and clear trace buffer
        for label in self.trace_labels:
            label.destroy()
        self.trace_buffer.clear()

    def exit(self):
        self.gui.destroy()

    def record_mouse_position(self, event):

        relx = (self.gui.winfo_pointerx() - self.gui.winfo_x()) / self.gui.winfo_width()
        rely = (self.gui.winfo_pointery() - self.gui.winfo_y()) / self.gui.winfo_height()

        # append coordinate to buffer only if euclidean distance exceeds minimum delta

        if not self.trace_buffer:
            self.trace_buffer.appendleft((relx, rely))
        else:
            prev_coords = self.trace_buffer[0]
            euclidean_dist = np.linalg.norm(np.array((relx, rely) - np.array((prev_coords))))
            if euclidean_dist > 0.05 or not self.trace_buffer:
                self.trace_buffer.appendleft((relx, rely))
                print('x={:.2f}, y={:.2f}'.format(relx, rely))

    def plot_trace(self):
        """ plot trace of last 100 mouse positions"""

        rgb_cols = [(255, yellow, 0) for yellow in np.linspace(255, 0, len(self.trace_buffer), dtype=int)]
        hex_cols = [rgb_to_hex(rgb) for rgb in rgb_cols]

        self.gui.unbind('<Motion>')  # temporarily unbind motion tracker
        for idx, (x, y) in enumerate(reversed(self.trace_buffer)):
            obj = Label(self.gui, text='', bg=hex_cols[idx])
            obj.place(relx=x, rely=y, relwidth=0.01, relheight=0.01)
            self.trace_labels.append(obj)
            self.gui.update()
            time.sleep(0.05)
        self.gui.bind('<Motion>', self.record_mouse_position)  # re-bind motion tracking after complete


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
    _display = Display(_keyboard, display_width=900, display_height=1200)
    _display.start_display()


