import tkinter as tk


class View:

    def __init__(self, root):
        """
        Parameters
        ----------
        root: tk.TK
        """
        self.root = root

    def periodic_callback(self, interval_secs, callback):
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
        callback()
        self.root.after(delay_ms=1000*interval_secs, callback=self.periodic_callback(interval_secs, callback))





