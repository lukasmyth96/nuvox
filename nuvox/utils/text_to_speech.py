import os
import sys
import time

from gtts import gTTS
import pygame


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

    tts = gTTS(text=text, lang='en')
    words = text.lower().split(' ')
    filename = '_'.join(words[:5]) + '.mp3'
    mp3_path = os.path.join(audo_file_dir, filename)

    tts.save(mp3_path)

    return mp3_path


def speak_text(text):
    """ Convert text to speech and then speak it"""
    audio_path = text_to_audio_file(text)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
