import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)30s - %(levelname)8s [%(funcName)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

from telegram.ext import (
    CommandHandler,
    Updater,
    Filters,
    MessageHandler,
    RegexHandler,
    CallbackQueryHandler,
)
from callbacks.handler import handle_callbacks
from commands.aproximacion.conversation_handler import msup_conversation
from commands.cartelera.command import cinearg
from commands.dolar.command import dolar_hoy
from commands.dolar_futuro.command import rofex
from commands.feedback.command import feedback_receiver
from commands.feriados.command import feriadosarg
from commands.hastebin.command import code_paster, CODELINK_PREFIX
from commands.hoypido.command import hoypido
from commands.misc.commands import format_code, link_ticket, default
from commands.meeting.command import show_meetings, delete_meeting
from commands.meeting.conversation_handler import meeting_conversation
from commands.partido.command import partido
from commands.pelicula.callback import pelicula_callback
from commands.pelicula.command import buscar_peli
from commands.pelicula.constants import PELICULA_REGEX
from commands.posiciones.command import posiciones
from commands.register.command import register, authorize, show_users
from commands.remindme.command import remind, reminder_callback
from commands.remindme.constants import REMINDERS_REGEX
from commands.remindme.persistence.job_loader import load_reminders
from commands.retro.handler import add_retro_item, show_retro_details, expire_retro_command
from commands.serie.callbacks import serie_callback_handler
from commands.serie.command import serie
from commands.snippets.command import (
    save_snippet,
    get_snippet,
    show_snippets,
    delete_snippet,
    get_snippet_command,
)
from commands.serie.constants import SERIE_REGEX
from commands.snippets.constants import SAVE_REGEX, GET_REGEX, DELETE_REGEX
from commands.start.command import start
from commands.subte.command import subte, modify_freq
from commands.subte.constants import SUBTE_UPDATES_CRON
from commands.subte.suscribers.command import suscribe, suscribers, unsuscribe
from commands.subte.updates.alerts import subte_updates_cron
from commands.tagger.all_tagger import tag_all, set_all_members
from commands.youtube.command import youtube_to_mp3
from commands.yts.callback_handler import handle_callback
from commands.yts.command import yts
from commands.yts.constants import YTS_REGEX
from utils.utils import error_handler, send_message_to_admin, signal_handler
from utils.constants import CODE_PREFIX, TICKET_REGEX, MINUTE

# Setup bot
updater = Updater(os.environ['PYTEL'], user_sig_handler=signal_handler)
dispatcher = updater.dispatcher

# Add commands handlers
start_handler = CommandHandler('start', start)
register_user = CommandHandler('register', register)
authorize_handler = CommandHandler('authorize', authorize, pass_args=True)
yt_handler = CommandHandler('yt2mp3', youtube_to_mp3, pass_args=True)
yt_handler_alt = CommandHandler('y', youtube_to_mp3, pass_args=True)
subte_suscriptions = CommandHandler('suscribe', suscribe, pass_args=True)
subte_desuscriptions = CommandHandler('unsuscribe', unsuscribe, pass_args=True)
subte_show_suscribers = CommandHandler('suscribers', suscribers)
show_users_handler = CommandHandler('users', show_users)
partido_handler = CommandHandler('partido', partido)
dolar_handler = CommandHandler('dolar', dolar_hoy, pass_chat_data=True)
dolar_futuro_handler = CommandHandler('rofex', rofex)
posiciones_handler = CommandHandler('posiciones', posiciones, pass_args=True)
subte_handler = CommandHandler('subte', subte)
modify_subte_freq = CommandHandler('setsubfreq', modify_freq, pass_job_queue=True, pass_args=True)
cartelera_handler = CommandHandler('cartelera', cinearg)
hoypido_handler = CommandHandler('hoypido', hoypido, pass_chat_data=True)
feriados_handler = CommandHandler('feriados', feriadosarg)
serie_handler = CommandHandler('serie', serie, pass_args=True, pass_chat_data=True)
pelis = CommandHandler('pelicula', buscar_peli, pass_args=True, pass_chat_data=True)
pelis_alt = CommandHandler('película', buscar_peli, pass_args=True, pass_chat_data=True)
yts_handler = CommandHandler('yts', yts, pass_chat_data=True)
show_meetings_handler = CommandHandler('meetings', show_meetings)
delete_meeting_handler = CommandHandler('delmeeting', delete_meeting, pass_args=True)
code_handler = RegexHandler(CODE_PREFIX, format_code, pass_groupdict=True)
save_snippet_handler = RegexHandler(SAVE_REGEX, save_snippet, pass_groupdict=True)
get_snippet_handler = RegexHandler(GET_REGEX, get_snippet, pass_groupdict=True)
snippet_get_command = CommandHandler('get', get_snippet_command, pass_args=True)
delete_snippet_handler = RegexHandler(DELETE_REGEX, delete_snippet, pass_groupdict=True)
show_snippets_handler = CommandHandler('snippets', show_snippets)
remind_me_handler = CommandHandler('remind', remind, pass_args=True, pass_chat_data=True)
hastebin_handler = RegexHandler(CODELINK_PREFIX, code_paster, pass_groupdict=True)
tag_all = MessageHandler(Filters.regex(r'@all'), tag_all)
edit_tag_all = CommandHandler('setall', set_all_members, pass_args=True)
tickets_handler = MessageHandler(Filters.regex(TICKET_REGEX), link_ticket)
generic_handler = MessageHandler(Filters.command, default)

# Add callback query handlers
serie_callback = CallbackQueryHandler(serie_callback_handler, pattern=SERIE_REGEX, pass_chat_data=True)
yts_callback_handler = CallbackQueryHandler(handle_callback, pattern=YTS_REGEX, pass_chat_data=True)
peliculas_callback = CallbackQueryHandler(pelicula_callback, pattern=PELICULA_REGEX, pass_chat_data=True)
reminders_callback_handler = CallbackQueryHandler(
    reminder_callback, pattern=REMINDERS_REGEX, pass_chat_data=True, pass_job_queue=True
)
callback_handler = CallbackQueryHandler(handle_callbacks, pass_chat_data=True)

# Add repeating jobs
cron_tasks = updater.job_queue
cron_tasks.run_repeating(subte_updates_cron, interval=5 * MINUTE, first=1 * MINUTE, context={}, name=SUBTE_UPDATES_CRON)

# Load reminders that were lost on bot restart (job_queue is not persistent)
loaded_reminders = load_reminders(updater.bot, cron_tasks)
logger.info(f"Recovered {loaded_reminders} reminders")


#  Associate commands with action.
dispatcher.add_handler(feedback_receiver)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(register_user)
dispatcher.add_handler(show_users_handler)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(partido_handler)
dispatcher.add_handler(dolar_handler)
dispatcher.add_handler(subte_suscriptions)
dispatcher.add_handler(modify_subte_freq)
dispatcher.add_handler(subte_desuscriptions)
dispatcher.add_handler(subte_show_suscribers)
dispatcher.add_handler(dolar_futuro_handler)
dispatcher.add_handler(posiciones_handler)
dispatcher.add_handler(subte_handler)
dispatcher.add_handler(cartelera_handler)
dispatcher.add_handler(add_retro_item)
dispatcher.add_handler(show_retro_details)
dispatcher.add_handler(expire_retro_command)
dispatcher.add_handler(pelis)
dispatcher.add_handler(pelis_alt)
dispatcher.add_handler(yts_handler)
dispatcher.add_handler(hoypido_handler)
dispatcher.add_handler(feriados_handler)
dispatcher.add_handler(serie_handler)
dispatcher.add_handler(yt_handler)
dispatcher.add_handler(yt_handler_alt)
dispatcher.add_handler(code_handler)
dispatcher.add_handler(save_snippet_handler)
dispatcher.add_handler(get_snippet_handler)
dispatcher.add_handler(snippet_get_command)
dispatcher.add_handler(show_snippets_handler)
dispatcher.add_handler(delete_snippet_handler)
dispatcher.add_handler(remind_me_handler)
dispatcher.add_handler(tag_all)
dispatcher.add_handler(show_meetings_handler)
dispatcher.add_handler(delete_meeting_handler)
dispatcher.add_handler(hastebin_handler)
dispatcher.add_handler(tickets_handler)
dispatcher.add_handler(edit_tag_all)


# Add callback handlers
dispatcher.add_handler(serie_callback)
dispatcher.add_handler(yts_callback_handler)
dispatcher.add_handler(reminders_callback_handler)
dispatcher.add_handler(peliculas_callback)


# Add Conversation handler
dispatcher.add_handler(msup_conversation)
dispatcher.add_handler(meeting_conversation)

dispatcher.add_handler(callback_handler)
dispatcher.add_handler(generic_handler)

dispatcher.add_error_handler(error_handler)

updater.start_polling()
logger.info('Listening humans as %s..' % updater.bot.username)
send_message_to_admin(updater.bot, "⚡️ I'm up and running ⚡️️")
updater.idle()
logger.info('Bot stopped gracefully')
