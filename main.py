import os
import logging

from telegram.ext import (
    CommandHandler,
    Updater,
)

from callbacks.handler import callback_handler
from commands.cartelera.command import cartelera_handler
from commands.dolar.command import dolar_handler
from commands.dolar_futuro.command import dolar_futuro_handler
from commands.feriados.command import feriados_handler, proximo_feriado_handler
from commands.github.command import github_handler
from commands.hastebin.command import hastebin_handler
from commands.hoypido.command import hoypido_handler
from commands.meeting.command import show_meetings_handler, delete_meeting_handler
from commands.misc.commands import code_handler, tickets_handler, generic_handler, show_source
from commands.partido.command import partido_handler
from commands.pelicula.callback import peliculas_callback
from commands.pelicula.command import pelis, pelis_alt
from commands.posiciones.command import posiciones_handler
from commands.register.command import register_user, show_users_handler, authorize_handler
from commands.remindme.command import remind_me_handler, reminders_callback_handler
from commands.serie.callbacks import serie_callback
from commands.serie.command import serie_handler
from commands.snippets.command import save_snippet_handler, get_snippet_handler, snippet_get_command, \
    show_snippets_handler, delete_snippet_handler
from commands.subte.command import modify_subte_freq, subte_handler
from commands.subte.suscribers.command import subte_suscriptions, subte_desuscriptions, subte_show_suscribers
from commands.youtube.command import yt_handler, yt_handler_alt
from commands.yts.callback_handler import yts_callback_handler
from commands.yts.command import yts_handler
from commands.aproximacion.conversation_handler import msup_conversation
from commands.feedback.command import feedback_receiver
from commands.meeting.conversation_handler import meeting_conversation
from commands.remindme.persistence.job_loader import load_reminders
from commands.retro.handler import add_retro_item, show_retro_details, expire_retro_command
from commands.start.command import start
from commands.subte.constants import SUBTE_UPDATES_CRON
from commands.subte.updates.alerts import subte_updates_cron
from commands.tagger.all_tagger import tag_all, edit_tag_all
from inlinequeries.snippets import inline_snippets
from utils.utils import error_handler, send_message_to_admin, signal_handler
from utils.constants import MINUTE

logging.basicConfig(format='%(asctime)s - %(name)30s - %(levelname)8s [%(funcName)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    # Setup bot
    updater = Updater(os.environ['PYTEL'], user_sig_handler=signal_handler)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)

    # Add repeating jobs
    cron_tasks = updater.job_queue
    cron_tasks.run_repeating(subte_updates_cron,
                             interval=5 * MINUTE,
                             first=50 * MINUTE,
                             context={},
                             name=SUBTE_UPDATES_CRON)

    # Load reminders that were lost on bot restart (job_queue is not persistent)
    loaded_reminders = load_reminders(updater.bot, cron_tasks)
    logger.info(f"Recovered {loaded_reminders} reminders")

    #  Associate commands with action.
    dispatcher.add_handler(feedback_receiver)
    dispatcher.add_handler(inline_snippets)
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
    dispatcher.add_handler(proximo_feriado_handler)
    dispatcher.add_handler(github_handler)
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
    dispatcher.add_handler(show_source)

    # Add callback handlers
    dispatcher.add_handler(serie_callback)
    dispatcher.add_handler(yts_callback_handler)
    dispatcher.add_handler(reminders_callback_handler)
    dispatcher.add_handler(peliculas_callback)

    # Add Conversation handler
    dispatcher.add_handler(msup_conversation)
    dispatcher.add_handler(meeting_conversation)

    # Add generics
    dispatcher.add_handler(callback_handler)
    dispatcher.add_handler(generic_handler)

    # Add error handler
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    logger.info('Listening humans as %s..' % updater.bot.username)
    updater.idle()
    logger.info('Bot stopped gracefully')


if __name__ == '__main__':
    main()
