import ast
import requests
import subprocess
import os
from tkinter import *

from definition import ROOT_DIR
from nuvox.timer_thread import MyTimer


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.master.geometry("450x600")

        self.canvas = Canvas(master=self.master,
                             width=self.master.winfo_screenwidth(),
                             height=self.master.winfo_screenheight())
        self.canvas.pack()
        self.eye_width = 20
        self.eyes = self.canvas.create_rectangle(0, 0, self.eye_width, self.eye_width, fill="blue")

        self.timer = MyTimer(timeout_secs=1000000,
                             interval_secs=0.01,
                             completion_callback=None,
                             periodic_callback=self.move_eyes)
        self.timer.start()

    def move_eyes(self, seconds_passed):
        screen_relx, screen_rely = get_eye_coords_relative_to_screen()  # get relative x y to screen

        window_x = (screen_relx * self.master.winfo_screenwidth() - self.master.winfo_x())
        window_y = (screen_rely * self.master.winfo_height() - self.master.winfo_y())

        w = self.eye_width / 2

        print('After {} seconds the eyes are at:'.format(seconds_passed), window_x, window_y)
        self.canvas.coords(self.eyes, window_x-w, window_y-w, window_x+w, window_y+w)  # so that the blob is centered on the eye rather than top left


def get_eye_coords_relative_to_screen():
    """
    Get current eye coords relative to entire screen
    Returns
    -------
    relx: float
        x coordinate relative to entire screen e.g. 0.5 means looking half way accross screen
    rely: float

    Raises
    ------
    NoGazeDataReturned: if no gaze data is returned
    """
    response = requests.get(url='http://localhost:3070')
    coords_string = response.content.decode('utf-8')

    if coords_string == 'null':
        raise NoGazeDataReturned

    coords_dict = ast.literal_eval(coords_string)
    relx = coords_dict['X'] / coords_dict['ViewportWidth']
    rely = coords_dict['Y'] / coords_dict['ViewportHeight']
    return relx, rely


class NoGazeDataReturned(Exception):
    pass


if __name__ == '__main__':

    c_file_path = os.path.join(ROOT_DIR, 'lib', 'Interaction_Streams_101.exe')
    subprocess.Popen(c_file_path)
    root = Tk()
    app = FullScreenApp(root)
    root.mainloop()

