#!/usr/bin/env python3

"""Canadian ACB calculator

An application with a graphical user interface to aid Canadians when
tracking the adjusted cost base of assets in investment portfolios.

Only dependencies are standard python packages.  Uses tkinter (Tcl/Tk)
for the GUI to manage cross-platform operation.
"""


import json
import os
import time

from . import cfg
from .nameserver import NameServer
from .pfo import PortfolioManager
from .ui import UserInterface


TIMESTAMP_FORMAT = "%Y-%m-%d:%H:%M:%S%z"


# pylint: disable=too-few-public-methods
class CanACB:
    """The application"""

    _NAMES = "** NAMES **"
    _PORTFOLIOS = "** PORTFOLIOS **"
    _PREFERENCES = "** PREFERENCES **"
    _APP_KEY = "app"
    _UI_KEY = "ui"
    _VERSION_STAMP = "version"
    _SAVED_STAMP = "saved"

    def __init__(self):
        """Loads saved data, then ...
        - creates a name server,
        - creates a portfolio manager,
        - launches the UI.
        """
        backing_store = load_from_json(cfg.DATA_FILE, dict)

        self._names = NameServer(backing_store.get(self._NAMES, {}))

        self._preferences = backing_store.get(self._PREFERENCES, {})
        if not isinstance(self._preferences, dict):
            raise TypeError("backing store: preferences damaged")
        for key in (self._APP_KEY, self._UI_KEY):
            if key not in self._preferences:
                self._preferences[key] = {}

        saved_pfos = backing_store.get(self._PORTFOLIOS, {})
        if not isinstance(saved_pfos, dict):
            raise TypeError("backing store: portfolios damaged")
        self._manager = PortfolioManager(saved_pfos)
        self._manager.mark_clean()

        UserInterface(
            self._names,
            self._preferences[self._UI_KEY],
            self._manager,
            self.save,
        )

    def save(self):
        """Saves preferences, names, and the portfolio manager.

        Returns None on success and an error message on failure.
        """
        self._preferences[self._APP_KEY][self._VERSION_STAMP] = cfg.APP_VERSION
        self._preferences[self._APP_KEY][self._SAVED_STAMP] = time.strftime(
            TIMESTAMP_FORMAT
        )

        serializable = {
            self._PREFERENCES: self._preferences,
            self._PORTFOLIOS: self._manager.serializable(),
            self._NAMES: self._names,
        }

        return save_to_json(serializable, cfg.DATA_FILE)


def load_from_json(filename, expected_type=dict):
    """Loads a json file.

    If the file doesn't exist or isn't valid json or contents look wrong,
    returns an empty version of the expected type.
    """
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            contents = json.load(file)
        if isinstance(contents, expected_type):
            return contents
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return expected_type()


def save_to_json(contents, filename):
    """Saves to a json file.

    Returns None if successful, or an error message string if not.
    """
    try:
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, mode="w", encoding="utf-8") as file:
            json.dump(contents, file)
        return None
    except OSError as exc:
        return str(exc)


def main():
    """Runs the app"""
    CanACB()


if __name__ == "__main__":
    main()
