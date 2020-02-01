import os
import threading

from gtts import gTTS
from mutagen.mp3 import MP3
import pygame


class TextToSpeech:

    def speak_text_in_new_thread(self, text):

        th = threading.Thread(target=lambda: self.speak_text(text))
        th.start()

    def speak_text(self, text):

        """ Convert text to speech and then speak it"""
        audio_path = self.text_to_audio_file(text)
        mp3 = MP3(audio_path)
        pygame.mixer.init()  # speeding up audio slightly

        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

    @staticmethod
    def text_to_audio_file(text):
        """
        Get audio file for speech
        Parameters
        ----------
        text: str

        Returns
        -------
        mp3_path: str
            path to mp3 file
        """

        # dir to save auido files
        audo_file_dir = '/home/luka/Documents/nuvox/tts_samples'

        tts = gTTS(text=text, lang='en', slow=False)
        words = text.lower().split(' ')
        filename = '_'.join(words[:5]) + '.mp3'
        mp3_path = os.path.join(audo_file_dir, filename)

        tts.save(mp3_path)

        return mp3_path



