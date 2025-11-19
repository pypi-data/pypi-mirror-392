#!/usr/bin/env python3

"""Canadian ACB calculator - configuration"""

import os

try:
    from xdg.BaseDirectory import xdg_data_home

    DATA_PATH = os.path.join(xdg_data_home, "canacb")

except ImportError:

    if "HOME" in os.environ:  # looks like Unix
        DATA_PATH = os.path.join(os.environ["HOME"], ".canacb")
    elif "APPDATA" in os.environ:  # looks like Windows
        DATA_PATH = os.path.join(os.environ["APPDATA"], "canacb")
    elif "PWD" in os.environ:  # current working directory
        DATA_PATH = os.environ["PWD"]
    else:  # last chance is this file's directory
        DATA_PATH = os.path.dirname(os.path.abspath(__file__))


APP_NAME = "CAN-ACB"
APP_VERSION = "0.4"
APP_AUTHORS = "Norbert Schlenker"
APP_LICENSE = "MIT"

SRC_FOLDER = os.path.dirname(os.path.abspath(__file__))
MENU_IMAGE = os.path.join(SRC_FOLDER, "images", "tinyleaf.png")
COPY_IMAGE = os.path.join(SRC_FOLDER, "images", "tinycopy.png")

DATA_FILE = os.path.join(DATA_PATH, "canacb.json")
