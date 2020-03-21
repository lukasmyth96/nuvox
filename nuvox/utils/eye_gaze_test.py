
import tkinter as tk

from nuvox.services.eye_gaze_server import EyeGazeServer, NoGazeDataReturned
from nuvox.config.config import Config


class EyeGazeTest(object):
    def __init__(self, root):
        """
        For testing the eye gaze
        Parameters
        ----------
        root:
        """
        self.root = root
        self.root.geometry("450x600")

        self.canvas = tk.Canvas(master=self.root,
                                width=self.root.winfo_screenwidth(),
                                height=self.root.winfo_screenheight())
        self.canvas.pack()
        self.eye_width = 20
        self.eyes = self.canvas.create_rectangle(0, 0, self.eye_width, self.eye_width, fill="blue")
        config = Config()
        self.eye_gaze_server = EyeGazeServer(host=config.GAZE_SERVER_HOST, exe_path=config.EXE_PATH)

    def run(self):
        self.eye_gaze_server.start_server()
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
        self.move_eyes()
        self.root.after(ms=100, func=self.start_periodic_callback)

    def move_eyes(self):

        try:
            screen_relx, screen_rely = self.eye_gaze_server.get_gaze_relative_to_screen()  # get relative x y to screen

            window_x = (screen_relx * self.root.winfo_screenwidth() - self.root.winfo_x())
            window_y = (screen_rely * self.root.winfo_height() - self.root.winfo_y())

            w = self.eye_width / 2
            self.canvas.coords(self.eyes, window_x - w, window_y - w, window_x + w, window_y + w)

        except NoGazeDataReturned:
            print('No gaze data returned!')


if __name__ == '__main__':

    root = tk.Tk()
    app = EyeGazeTest(root)
    app.run()

