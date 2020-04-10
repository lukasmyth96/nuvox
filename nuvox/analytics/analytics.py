from datetime import datetime
import os
import itertools

import numpy as np

from nuvox.utils.io import pickle_load
from nuvox.analytics.session import Session


class Analytics:

    def __init__(self):

        self.sessions = []

    def __repr__(self):
        return 'session_loading_fixtures: {}'.format(len(self))

    def __len__(self):
        return len(self.sessions)

    def __iter__(self):
        for swype in self.sessions:
            yield swype

    def __getitem__(self, item):
        return self.sessions[item]

    def append(self, session):
        """
        Parameters
        ----------
        session: Session
        """
        if not isinstance(session, Session):
            raise ValueError('can only append instances of the Session class')
        self.sessions.append(session)

    def load_sessions(self, directory, start_date=None, end_date=None):
        """
        Load saved session_loading_fixtures - between start and end date (inclusive) if specified
        Parameters
        ----------
        directory: str
        start_date: str, optional
            in format YYYY_MM_DD (same for end_date_
        end_date: str, optional

        Raises
        -------
        ValueError
            if start_date or end_date are not None and do not fit format
        """
        try:
            start_date = datetime.strptime(start_date, '%Y_%m_%d') if start_date is not None else datetime.min
            end_date = datetime.strptime(end_date, '%Y_%m_%d') if end_date is not None else datetime.max
        except ValueError:
            raise ValueError('Invalid date or format - must be YYYY_MM_DD')
        for filename in os.listdir(directory):
            date = datetime.strptime(filename.split('_T')[0], '%Y_%m_%d')
            if start_date <= date <= end_date:
                session = pickle_load(os.path.join(directory, filename))
                self.append(session)

    def mean_accepted_word_rank(self):
        """
        Returns the mean across all swypes in all session_loading_fixtures of the rank of the accepted word within list ranked
        suggestions for that swype.
        Parameters
        ----------
        Returns
        -------
        mean_rank: float
        """
        return np.mean(list(itertools.chain.from_iterable([[swype.accepted_word_rank for swype in session]
                                                           for session in self.sessions])))

    def top_n_accuracy(self, n=1):
        """
        Returns the % of all swypes for which the accepted word was in the top-n suggestions
        Parameters
        ----------
        n: int

        Returns
        -------
        accuracy: float
        """
        return np.mean(list(itertools.chain.from_iterable([[swype.accepted_word in swype.ranked_suggestions[:n]
                                                           for swype in session]
                                                           for session in self.sessions])))
