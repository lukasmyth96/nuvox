import tkinter as tk

import numpy as np

widget_type_to_class = {'button': tk.Button,
                        'text': tk.Text}


class View:

    def __init__(self, config):
        """
        Parameters
        ----------
        config: nuvox.config.config.Config
        """
        self.root = tk.Tk()
        self.config = config
        self.key_id_to_widget = {}
        self.periodic_callback = None

        num_colour_increments = np.math.ceil(config.REQ_DWELL_TIME / config.GAZE_INTERVAL)
        rgb_increment_arr = (np.array(config.DEFAULT_BG) - np.array(config.HIGHLIGHT_BG)) / num_colour_increments
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
        self.root.after(ms=1000*self.config.GAZE_INTERVAL, func=self.start_periodic_callback)

    def create_widgets(self, keyboard):
        """
        Create widget for each key in keyboard
        Parameters
        ----------
        keyboard: nuvox.keyboard.Keyboard
        """
        for key in keyboard.keys:
            text = ' '.join(key.contents).upper()
            widget = widget_type_to_class[key.widget_type](master=self.root,
                                                           text=text,
                                                           fg=self.config.TEXT_COLOUR,
                                                           bg=self.config.DEFAULT_BG,
                                                           font=("{} {}".format(self.config.FONT, self.config.FONT_SIZE)))
            self.key_id_to_widget[key.key_id] = widget

    def update_display_text(self, new_text):
        widget = self.key_id_to_widget['display']
        widget.configure(text=new_text)

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
        widget = self.key_id_to_widget[key_id]
        hex = rgb_to_hex(rgb)
        widget.configure(bg=hex, activebackground=hex)


def rgb_to_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


def hex_to_rgb(hex):
    """ Converts hex string to rgb tuple"""
    h = hex.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))





