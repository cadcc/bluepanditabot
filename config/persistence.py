from os import path

from telegram.ext import PicklePersistence

persistence = PicklePersistence(filepath=path.relpath('db'), on_flush=False)
