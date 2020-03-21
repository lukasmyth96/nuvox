import os
import threading

import pygame

from definition import ROOT_DIR


class SFX:

    def __init__(self):

        self.click_on_mp3 = os.path.join(ROOT_DIR, 'nuvox', 'resources', 'click_on.mp3')
        self.click_off_mp3 = os.path.join(ROOT_DIR, 'nuvox', 'resources', 'click_off.mp3')

    def button_click_sfx_in_new_thread(self, type='select'):
        """
        Play button select / unselect sfx in new thread
        Parameters
        ----------
        type: str
            'select' or 'unselect'
        """
        assert type in ['select', 'unselect']

        def button_click(type):
            if type == 'select':
                mp3_path = self.click_on_mp3
            else:
                mp3_path = self.click_off_mp3

            pygame.mixer.init()
            pygame.mixer.music.load(mp3_path)
            pygame.mixer.music.play()

        th = threading.Thread(target=lambda: button_click(type))
        th.start()