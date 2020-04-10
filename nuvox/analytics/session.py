from datetime import datetime
import os
import subprocess

from nuvox.utils.io import pickle_save
from nuvox.analytics.swype import Swype


class Session:

    def __init__(self, config):
        """
        Session stores the analytics data from a single user session.
        Parameters
        ----------
        config: nuvox.config.config.Config
        """

        self.swypes = []

        # Store information about state at runtime
        self.output_dir = config.ANALYTICS_OUTPUT_DIR
        self.config = config
        self.start_time = datetime.now().strftime("%Y_%m_%d_T%H_%M_%S")
        self.commit = subprocess.check_output(["git", "describe", "--always"]).strip().decode('utf-8')

    def __repr__(self):
        return 'start time: {} \ncommit: {} \nswypes: {}'.format(self.start_time, self.commit, len(self))

    def __len__(self):
        return len(self.swypes)

    def __iter__(self):
        for swype in self.swypes:
            yield swype

    def __getitem__(self, item):
        return self.swypes[item]

    def append(self, swype):
        """
        Add swype to session
        Parameters
        ----------
        swype: nuvox.analytics.swype.Swype
        """
        if not isinstance(swype, Swype):
            raise ValueError('can only append instances of the Swype class')
        self.swypes.append(swype)

    def save(self):
        filename = '{}.pkl'.format(self.start_time)
        pickle_save(os.path.join(self.output_dir, filename), self)




