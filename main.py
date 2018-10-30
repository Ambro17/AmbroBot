import os
import logging

from telegram.ext import (
    CommandHandler,
    Updater,
    Filters,
    MessageHandler,
    RegexHandler,
    CallbackQueryHandler,
)
from callbacks.handler import handle_callbacks
from commands.cartelera.command import cinearg
from commands.dolar.command import dolar_hoy
from commands.dolar_futuro.command import dolar_futuro
from commands.feriados.command import feriados
from commands.hoypido.command import hoypido
from commands.misc.commands import format_code, link_ticket, default
from commands.partido.command import partido
from commands.pelicula.command import buscar_peli
from commands.posiciones.command import posiciones
from commands.serie.callbacks_handler import serie_callback_handler
from commands.serie.command import serie
from commands.snippets.command import save_snippet, get_snippet, show_snippets, delete_snippet
from commands.serie.constants import SERIE_REGEX
from commands.snippets.constants import SAVE_REGEX, GET_REGEX, DELETE_REGEX
from commands.start.command import start
from commands.subte.command import subte
from commands.tagger.all_tagger import tag_all, set_all_members
from commands.yts.callback_handler import handle_callback
from commands.yts.command import yts
from commands.yts.constants import YTS_REGEX
from utils.command_utils import error_handler
from utils.constants import CODE_PREFIX, TICKET_REGEX

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Setup bot
updater = Updater(os.environ['PYTEL'])
dispatcher = updater.dispatcher

# Add commands handlers
start_handler = CommandHandler('start', start)
partido_handler = CommandHandler('partido', partido)
dolar_handler = CommandHandler('dolar', dolar_hoy, pass_chat_data=True)
dolar_futuro_handler = CommandHandler('fdolar', dolar_futuro)
posiciones_handler = CommandHandler('posiciones', posiciones, pass_args=True)
subte_handler = CommandHandler('subte', subte)
cartelera_handler = CommandHandler('cartelera', cinearg)
hoypido_handler = CommandHandler('hoypido', hoypido, pass_chat_data=True)
feriados_handler = CommandHandler('feriados', feriados, pass_args=True)
serie_handler = CommandHandler('serie', serie, pass_args=True, pass_chat_data=True)
pelis = CommandHandler('pelicula', buscar_peli, pass_args=True, pass_chat_data=True)
yts_handler = CommandHandler('yts', yts, pass_chat_data=True)
save_snippet_handler = RegexHandler(SAVE_REGEX, save_snippet, pass_groupdict=True)
get_snippet_handler = RegexHandler(GET_REGEX, get_snippet, pass_groupdict=True)
delete_snippet_handler = RegexHandler(DELETE_REGEX, delete_snippet, pass_groupdict=True)
show_snippets_handler = CommandHandler('snippets', show_snippets)
tag_all = MessageHandler(Filters.regex(r'@all'), tag_all)
edit_tag_all = CommandHandler('setall', set_all_members, pass_args=True)
code_handler = RegexHandler(CODE_PREFIX, format_code, pass_groupdict=True)
tickets_handler = RegexHandler(TICKET_REGEX, link_ticket, pass_groupdict=True)
generic_handler = MessageHandler(Filters.command, default)

# Add callback query handlers
serie_callback = CallbackQueryHandler(serie_callback_handler, pattern=SERIE_REGEX, pass_chat_data=True)
yts_callback_handler = CallbackQueryHandler(handle_callback, pattern=YTS_REGEX, pass_chat_data=True)
callback_handler = CallbackQueryHandler(handle_callbacks, pass_chat_data=True)

#  Associate commands with actions.
dispatcher.add_handler(start_handler)
dispatcher.add_handler(partido_handler)
dispatcher.add_handler(dolar_handler)
dispatcher.add_handler(dolar_futuro_handler)
dispatcher.add_handler(posiciones_handler)
dispatcher.add_handler(subte_handler)
dispatcher.add_handler(cartelera_handler)
dispatcher.add_handler(pelis)
dispatcher.add_handler(yts_handler)
dispatcher.add_handler(hoypido_handler)
dispatcher.add_handler(feriados_handler)
dispatcher.add_handler(serie_handler)
dispatcher.add_handler(serie_callback)
dispatcher.add_handler(yts_callback_handler)
dispatcher.add_handler(callback_handler)
dispatcher.add_handler(code_handler)
dispatcher.add_handler(save_snippet_handler)
dispatcher.add_handler(get_snippet_handler)
dispatcher.add_handler(show_snippets_handler)
dispatcher.add_handler(delete_snippet_handler)
dispatcher.add_handler(tag_all)
dispatcher.add_handler(edit_tag_all)
dispatcher.add_handler(tickets_handler)
dispatcher.add_handler(generic_handler)

dispatcher.add_error_handler(error_handler)

updater.start_polling()
logger.info('Listening humans..')
