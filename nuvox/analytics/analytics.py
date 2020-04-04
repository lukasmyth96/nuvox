from datetime import datetime
import os

from nuvox.utils.io import pickle_load
from nuvox.analytics.session import Session


class Analytics:

    def __init__(self):

        self.sessions = []

    def __repr__(self):
        return 'sessions: {}'.format(len(self))

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
        Load saved sessions - between start and end date (inclusive) if specified
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



