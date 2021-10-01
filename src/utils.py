# Copyright (c) 2020-2029 Alex Carrega <contact@alexcarrega.com>
# author: Alex Carrega <contact@alexcarrega.com>

# General
from datetime import datetime


class DateTime:
    FORMAT = '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def from_str(date_time_str, format=FORMAT):
        """Get a datetime object from the string.

        :params date_time_str: datetime in string
        :params format: datetime format
        :returns: datetime object
        """
        return datetime.strptime(date_time_str, format)

    @staticmethod
    def to_str(date_time=None, format=FORMAT):
        """Convert the datetime to string in the given format.

        :params data_time: datetime input
        :params format: datetime format
        :returns: datetime string in the given format
        """
        if date_time is None:
            date_time = datetime.utcnow()
        return date_time.strftime(format)
