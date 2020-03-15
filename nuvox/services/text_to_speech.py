import os
import threading

from gtts import gTTS
import pygame


class TextToSpeech:

    def __init__(self, audio_file_dir):
        """
        Text to speech
        Parameters
        ----------
        audio_file_dir: str
            dir in which to save audio files
        """
        self.audio_file_dir = audio_file_dir
        if not os.path.isdir(audio_file_dir):
            os.mkdir(audio_file_dir)

    def speak_text_in_new_thread(self, text):

        th = threading.Thread(target=lambda: self.speak_text(text))
        th.start()

    def speak_text(self, text):

        """ Convert text to speech and then speak it"""
        audio_path = self.text_to_audio_file(text)
        pygame.mixer.init()  # speeding up audio slightly
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

    def text_to_audio_file(self, text):
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

        tts = gTTS(text=text, lang='en', slow=False)
        words = text.lower().split(' ')
        filename = '_'.join(words[:5]) + '.mp3'
        mp3_path = os.path.join(self.audio_file_dir, filename)

        tts.save(mp3_path)

        return mp3_path




