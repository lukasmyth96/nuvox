
from distutils.util import strtobool
import json
import logging
import os
import pickle


def pickle_save(filename, an_object):

    with open(filename, 'wb') as output_file:
        pickle.dump(an_object, output_file, protocol=4)


def pickle_load(filename):

    with open(filename, 'rb') as input_file:
        an_object = pickle.load(input_file, encoding='bytes')

    return an_object

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return data


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as text_file:
        data = text_file.read()

    return data


def write_text_file(file_path, a_string):
    with open(file_path, 'w', encoding='utf-8') as text_file:
        chars_written_int = text_file.write(a_string)

    return chars_written_int


def write_json_file(file_path, data_dict):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, ensure_ascii=False, sort_keys=True, indent=4)


def initialise_logger(log_file_path=None):
    logger = logging.getLogger('main_app')
    logger.setLevel(logging.INFO)

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt="%Y-%m-%d %H:%M:%S")

    # Get handler names
    handler_names = [log_handler.name for log_handler in logger.handlers]

    if ('file_handler' not in handler_names) and (log_file_path is not None):
        # create the logging file handler
        log_file_directory = os.path.dirname(log_file_path)
        if not os.path.exists(log_file_directory):
            os.makedirs(log_file_directory)
        logger_fh = logging.FileHandler(log_file_path, encoding='utf-8')
        logger_fh.setFormatter(log_formatter)
        logger_fh.set_name('file_handler')
        logger.addHandler(logger_fh)

    if 'console' not in handler_names:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.set_name('console')
        logger.addHandler(console_handler)

    return logger