import logging
import sys
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from os import path

# 3 MB max files, up to 5 backup files.
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s - %(message)s',
                    level=logging.INFO,
                    handlers=[RotatingFileHandler(path.relpath('bot.log'), mode='a', maxBytes=3*1024*1024,
                                                  backupCount=5, encoding=None, delay=0),
                              StreamHandler(sys.stdout)])

# Libraries only log warnings and errors (httpx logs every polling request at INFO).
for name in ('httpx', 'httpcore', 'telegram', 'apscheduler'):
    logging.getLogger(name).setLevel(logging.WARNING)

logger = logging.getLogger('BluePanditaBot')


def log_command(update):
    logger.info(f"{update.message.text!r} from {update.message.chat_id}")
