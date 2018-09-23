import os
import logging
from telegram.ext import (
    CommandHandler,
    Updater,
    Filters,
    MessageHandler)
from commands import (
    dolar_hoy,
    partido,
    ping,
    dolar_futuro,
    default,
    posiciones
)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#  Add Commands.
updater = Updater(token=os.environ['pytel'])
dispatcher = updater.dispatcher
partido_handler = CommandHandler('partido', partido, pass_args=True)
ping_handler = CommandHandler('ping', ping)
dolar_handler = CommandHandler('dolar', dolar_hoy)
dolar_futuro_handler = CommandHandler('fdolar', dolar_futuro)
posiciones_hanlder = CommandHandler('posiciones', posiciones, pass_args=True)
generic_handler = MessageHandler(Filters.command, default)

#  Associate command with actions.
dispatcher.add_handler(dolar_handler)
dispatcher.add_handler(partido_handler)
dispatcher.add_handler(dolar_futuro_handler)
dispatcher.add_handler(posiciones_hanlder)
dispatcher.add_handler(generic_handler)

updater.start_polling()
