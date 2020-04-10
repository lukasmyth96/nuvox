
import json
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


