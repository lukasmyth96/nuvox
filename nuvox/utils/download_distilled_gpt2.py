import argparse
import os
import io
import json
import requests

import h5py

from definition import ROOT_DIR


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dest_dir', type=str,
                        default='models/language_models/distilled_gpt2_redownloaded',
                        help='dir in which to save the downloaded files - relative to the ROOT DIR')

    pargs = parser.parse_args()

    filename_to_url = {'config.json': 'https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-config.json',
                       'vocab.json': 'https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-vocab.json',
                       'merges.txt': 'https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-merges.txt',
                       'tf_model.h5': 'https://s3.amazonaws.com/models.huggingface.co/bert/distilgpt2-tf_model.h5'}

    with h5py.File('test.hdf5', 'a') as f:
        dset = f.create_dataset("default", data=arr)

    for filename, url in filename_to_url.items():

        dest_filepath = os.path.join(ROOT_DIR, pargs.dest_dir, filename)
        response = requests.get(url=url)

        if filename.endswith('json'):
            with open(dest_filepath, 'w+') as fp:
                json.dump(response.json(), fp)

        elif filename.endswith('txt'):
            with open(dest_filepath, 'w+') as fp:
                fp.write(response.content.decode('utf-8'))

        else:
            with h5py.File('test.hdf5', 'w') as f:
                content = io.BytesIO(response.content)
                dset = f.create_dataset("default", data=content)





