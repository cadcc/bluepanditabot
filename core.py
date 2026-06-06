from telegram.ext import ApplicationBuilder

from config.auth import token
from config.persistence import persistence

application = ApplicationBuilder().token(token).persistence(persistence).build()
