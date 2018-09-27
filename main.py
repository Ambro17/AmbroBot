import os
import logging
import re

from telegram.ext import (
    CommandHandler,
    Updater,
    Filters,
    MessageHandler,
    RegexHandler,
)
from commands import (
    dolar_hoy,
    partido,
    ping,
    dolar_futuro,
    default,
    posiciones,
    link_ticket,
    subte,
    format_code,
)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TICKET_REGEX = re.compile(r'((t|osp\-?)(?P<ticket>\d{5,6}))', re.IGNORECASE)
# Text starting with ~, \c, \code or $ will be monospaced formatted
CODE_PREFIX = re.compile(r'^(~|\\code|\$|\\c) (?P<code>[\s\S]+)')

#  Add Commands.
updater = Updater(token=os.environ['pytel'])
dispatcher = updater.dispatcher
partido_handler = CommandHandler('partido', partido, pass_args=True)
ping_handler = CommandHandler('ping', ping)
dolar_handler = CommandHandler('dolar', dolar_hoy)
dolar_futuro_handler = CommandHandler('fdolar', dolar_futuro)
posiciones_hanlder = CommandHandler('posiciones', posiciones, pass_args=True)
subte_handler = CommandHandler('subte', subte)
generic_handler = MessageHandler(Filters.command, default)
code_handler = RegexHandler(CODE_PREFIX, format_code, pass_groupdict=True)
tickets_handler = RegexHandler(TICKET_REGEX, link_ticket, pass_groupdict=True)

#  Associate command with actions.
dispatcher.add_handler(dolar_handler)
dispatcher.add_handler(partido_handler)
dispatcher.add_handler(dolar_futuro_handler)
dispatcher.add_handler(posiciones_hanlder)
dispatcher.add_handler(subte_handler)
dispatcher.add_handler(generic_handler)
dispatcher.add_handler(tickets_handler)
dispatcher.add_handler(code_handler)

updater.start_polling()
logger.info('Listening humans..')