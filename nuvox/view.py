import tkinter as tk
import time

import numpy as np


class View:

    def __init__(self, config):
        """
        Parameters
        ----------
        config: nuvox.config.config.Config
        """
        self.config = config
        self.root = tk.Tk()
        self.configure_window()
        self.key_id_to_widget = {}
        self.periodic_callback = None

        num_colour_increments = np.math.ceil(config.REQ_DWELL_TIME / config.GAZE_INTERVAL)
        rgb_increment_arr = (np.array(config.HIGHLIGHT_BG) - np.array(config.DEFAULT_BG)) / num_colour_increments
        self.rgb_increment = tuple([int(val) for val in rgb_increment_arr])

    def start_loop(self):
        if self.periodic_callback is None:
            raise ValueError('Cannot start app until periodic callback has been set in View')

        self.start_periodic_callback()
        self.root.mainloop()

    def start_periodic_callback(self):
        """
        Periodic callback - used to sample either eye gaze or mouse position every n seconds
        Parameters
        ----------
        interval_secs: float
            number of seconds between succesive callbacks calls
        callback: function
            function to be called every n=interval_secs seconds
        """
        # make function call and then call this function again after delay
        self.periodic_callback()
        self.root.after(ms=int(1000*self.config.GAZE_INTERVAL), func=self.start_periodic_callback)

    def create_widgets(self, keyboard):
        """
        Create widget for each key in keyboard
        Parameters
        ----------
        keyboard: nuvox.keyboard.Keyboard
        """
        for key in keyboard.keys:
            text = ' '.join(key.contents).upper()
            widget = tk.Button(master=self.root,
                               text=text,
                               fg=rgb_to_hex(self.config.TEXT_COLOUR),
                               bg=rgb_to_hex(self.config.DEFAULT_BG),
                               font=("{} {}".format(self.config.FONT, self.config.BUTTON_FONT_SIZE)))
            widget.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)

            if key.key_id == 'display':
                widget.configure(anchor=tk.W,
                                 font="{} {}".format(self.config.FONT, self.config.DISPLAY_FONT_SIZE))

            widget.place()
            self.key_id_to_widget[key.key_id] = widget

    def configure_window(self):
        self.root.configure(background=self.config.DISPLAY_BG_COLOUR)
        self.root.title('nuvox keyboard')
        self.root.geometry("{}x{}+350+50".format(self.config.DISPLAY_WIDTH,
                                                 self.config.DISPLAY_HEIGHT))
        self.root.resizable(width=self.config.RESIZABLE, height=self.config.RESIZABLE)
        self.root.attributes("-topmost", self.config.FORCE_ON_TOP)

    def update_display_text(self, new_text):
        widget = self.key_id_to_widget['display']
        widget.configure(text=new_text)

    def flash_pred_word(self, key_id, word):
        """ flash predicted word on last key in focus"""
        widget = self.key_id_to_widget[key_id]
        current_text = widget.cget('text')
        widget.configure(text=word, font="{} {}".format(self.config.FONT, self.config.BUTTON_FONT_SIZE+6))
        self.root.update()
        time.sleep(self.config.PRED_FLASH_DURATION)
        widget.configure(text=current_text, font="{} {}".format(self.config.FONT, self.config.BUTTON_FONT_SIZE))  # restore current text

    def increment_widget_colour(self, key_id):
        widget = self.key_id_to_widget[key_id]
        current_hex = widget.cget('bg')
        current_rgb = hex_to_rgb(current_hex)
        new_rgb = tuple([curr + incr for curr, incr in zip(current_rgb, self.rgb_increment)])
        self.change_widget_colour(key_id, rgb=new_rgb)

    def reset_widget_colour(self, key_id):
        self.change_widget_colour(key_id, rgb=self.config.DEFAULT_BG)

    def change_widget_colour(self, key_id, rgb):
        """
        Parameters
        ----------
        key_id: str
        rgb: tuple
        """
        if is_valid_rgb(rgb):
            widget = self.key_id_to_widget[key_id]
            hex = rgb_to_hex(rgb)
            widget.configure(bg=hex, activebackground=hex)
        else:
            print('Warning attempted to change to invalid rgb: ', rgb)


def rgb_to_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


def is_valid_rgb(rgb):
    return isinstance(rgb, tuple) and all([isinstance(val, int) for val in rgb]) and all([0 <= val <= 255 for val in rgb])

def hex_to_rgb(hex):
    """ Converts hex string to rgb tuple"""
    h = hex.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))





