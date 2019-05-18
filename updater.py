import os
from telegram.ext import Updater
from utils.utils import signal_handler


updater = Updater(os.environ['PYTEL'], user_sig_handler=signal_handler)
elbot = updater.dispatcher
