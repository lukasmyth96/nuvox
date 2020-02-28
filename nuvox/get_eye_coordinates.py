import ast
import requests
import subprocess
from subprocess import check_output
import time
import os
from tkinter import *

from nuvox.timer_thread import MyTimer


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self.master.geometry("{}x{}".format(master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))

        self.canvas = Canvas(master=self.master,
                             width=self.master.winfo_screenwidth()-pad,
                             height=self.master.winfo_screenheight()-pad)
        self.canvas.pack()
        self.eye_width = 20
        self.eyes = self.canvas.create_rectangle(0, 0, self.eye_width, self.eye_width, fill="blue")

        self.timer = MyTimer(timeout_secs=1000000,
                             interval_secs=0.01,
                             completion_callback=None,
                             periodic_callback=self.move_eyes)
        self.timer.start()

    def move_eyes(self, seconds_passed):
        x, y = get_eye_coords()
        x = x / 2  # account for scaling issues
        y = y / 2
        w = self.eye_width / 2

        print('After {} seconds the eyes are at:'.format(seconds_passed), x, y)
        self.canvas.coords(self.eyes, x-w, y-w, x+w, y+w)  # so that the blob is centered on the eye rather than top left


def get_eye_coords():
    """
    Get current eye coords
    Returns
    -------
    x: float
    y: float
    """
    response = requests.get(url='http://localhost:3070')
    coords_string = response.content.decode('utf-8')
    coords_dict = ast.literal_eval(coords_string)
    x = coords_dict['X']
    y = coords_dict['Y']
    return x, y


if __name__ == '__main__':

    c_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib', 'Interaction_Streams_101.exe')
    subprocess.Popen(c_file_path)
    root = Tk()
    app = FullScreenApp(root)
    root.mainloop()

