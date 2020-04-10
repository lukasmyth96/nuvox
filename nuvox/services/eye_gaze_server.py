import ast
import ctypes
import requests
import subprocess


class NoGazeDataReturned(Exception):
    pass


class EyeGazeServer:

    def __init__(self, host, exe_path):
        """
        Wrapper class for eye gaze HTTP server that's implemented in /eye_gaze_server/Eye_Gaze_Server.exe

        NOTE - the server can only be run with administrator rights
        Parameters
        ----------
        host: str
            url on which gaze server will run
        exe_path: str
            path to .exe file to run server
        """
        self.host = host
        self.exe_path = exe_path
        self.process = None

    def start_server(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise OSError('You must run python with administrator rights to start the eye server')
        self.process = subprocess.Popen(self.exe_path)

    def get_gaze_relative_to_screen(self):
        """
        Returns current eye coords x, y relative to entire screen
        Returns
        -------
        relx: float
            x coordinate relative to entire screen e.g. 0.5 means looking half way across screen
        rely: float

        Raises
        ------
        NoGazeDataReturned: if no gaze data is returned
        """
        response = requests.get(url=self.host)
        coords_string = response.content.decode('utf-8')

        if coords_string == 'null':
            raise NoGazeDataReturned

        coords_dict = ast.literal_eval(coords_string)
        relx = coords_dict['X'] / coords_dict['ViewportWidth']
        rely = coords_dict['Y'] / coords_dict['ViewportHeight']
        return relx, rely

