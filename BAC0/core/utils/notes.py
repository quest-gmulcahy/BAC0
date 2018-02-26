
# -*- coding: utf-8 -*-
"""
Notes and logger decorator to be used on class

This will add a "notes" object to the class and will allow
logging feature at the same time.
Goal is to be able to access quickly to important informations for
the web interface.

"""
#--- standard Python modules ---
from collections import namedtuple
from datetime import datetime
import logging
from logging import FileHandler

import os
from os.path import expanduser, join

#--- 3rd party modules ---
try:
    import pandas as pd
    _PANDAS = True
except ImportError:
    _PANDAS = False


def note_and_log(cls):
    """
    This will be used as a decorator on class to activate
    logging and store messages in the variable cls._notes
    This will allow quick access to events in the web app.

    A note can be added to cls._notes without logging if passing
    the argument log=false to function note()
    Something can be logged without addind a note using function log()
    """
    if hasattr(cls, 'DEBUG_LEVEL'):
        if cls.DEBUG_LEVEL == 'debug':
            file_level = logging.DEBUG
            console_level = logging.DEBUG
        elif cls.DEBUG_LEVEL == 'info':
            file_level = logging.INFO
            console_level = logging.INFO
    else:
        file_level = logging.WARNING
        console_level = logging.WARNING
    # Notes object
    cls._notes = namedtuple('_notes', ['timestamp', 'notes'])
    cls._notes.timestamp = []
    cls._notes.notes = []

    # Defining log object
    logname = '%s | %s' % (cls.__module__, cls.__name__)
    cls._log = logging.getLogger(logname)
    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    _PERMISSION_TO_WRITE = True
    logUserPath = expanduser('~')
    logSaveFilePath = join(logUserPath, '.BAC0')

    logFile = join(logSaveFilePath, 'BAC0.log')
    if not os.path.exists(logSaveFilePath):
        try:
            os.makedirs(logSaveFilePath)
        except:
            _PERMISSION_TO_WRITE = False
    if _PERMISSION_TO_WRITE:
        fh = FileHandler(logFile)
        fh.setLevel(file_level)
        fh.setFormatter(formatter)

    ch.setFormatter(formatter)
    # Add handlers the first time only...
    if not len(cls._log.handlers):
        if _PERMISSION_TO_WRITE:
            cls._log.addHandler(fh)
        cls._log.addHandler(ch)

    def log(self, txt, args=None, *, level=logging.DEBUG):
        """
        Add a log entry...no note
        """
        if not txt:
            raise ValueError('Provide something to log')
        msg = (txt % args) if args else txt
        cls._log.log(self.get_level(level), msg)

    def log_info(self, txt, args=None):
        self.log(txt, args, level=logging.INFO)

    def log_debug(self, txt, args=None):
        self.log(txt, args, level=logging.DEBUG)

    def log_warning(self, txt, args=None):
        self.log(txt, args, level=logging.WARNING)

    def log_error(self, txt, args=None):
        self.log(txt, args, level=logging.ERROR)

    def log_critical(self, txt, args=None):
        self.log(txt, args, level=level.CRITIC)

    def note(self, txt, args=None, *, level=logging.INFO, log=True):
        """
        Add note to the object. By default, the note will also
        be logged

        :param note: (str) The note itself
        :param args: arguments for msg
        :param level: (logging.level)
        :param log: (boolean) Enable or disable logging of note
        """
        if not txt:
            raise ValueError('Provide something to log')
        msg = (txt % args) if args else txt
        cls._notes.timestamp.append(datetime.now())
        cls._notes.notes.append(msg)
        if log:
            self.log(msg, level=self.get_level(level))

    @property
    def notes(self):
        """
        Retrieve notes list as a Pandas Series if possible... or a dict.
        """
        if not _PANDAS:
            return dict(zip(self._notes.timestamp, self._notes.notes))
        return pd.Series(self._notes.notes, index=self._notes.timestamp)

    def clear_notes(self):
        """
        Clear notes object
        """
        cls._notes.timestamp = []
        cls._notes.notes = []

    def get_level(self, lvl):
        SUPPORTED_LEVELS = [logging.INFO,
                            logging.DEBUG,
                            logging.WARNING,
                            logging.ERROR,
                            logging.CRITICAL
                            ]
        LEVELS = {'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL,
                  }
        if lvl in SUPPORTED_LEVELS:
            return lvl
        else:
            try:
                return LEVELS[lvl.lower()]
            except IndexError:
                raise IndexError('Wrong level provided for logging')

    # Add the functions to the decorated class
    cls.clear_notes = clear_notes
    cls.note = note
    cls.notes = notes
    cls.log = log
    cls.log_debug = log_debug
    cls.log_info = log_info
    cls.log_warning = log_warning
    cls.log_error = log_error
    cls.get_level = get_level
    return cls
