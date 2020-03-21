from io import BytesIO
import threading

from gtts import gTTS
import pygame


class TextToSpeech:

    def __init__(self):
        """
        Text to speech
        Parameters
        ----------
        audio_file_dir: str
            dir in which to save audio files
        """
        pygame.init()

    def speak_text_in_new_thread(self, text):
        th = threading.Thread(target=lambda: self.speak_text(text))
        th.start()

    @staticmethod
    def speak_text(text):
        tts = gTTS(text=text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)





