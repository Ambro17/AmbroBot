import logging
import os
from importlib import import_module

from updater import updater, elbot

from callbacks.handler import callback_handler
from commands.pelicula.callback import peliculas_callback
from commands.serie.callbacks import serie_callback
from commands.yts.callback_handler import yts_callback_handler
from commands.aproximacion.command import msup_conversation
from commands.feedback.command import feedback_receiver
from commands.meeting.conversation_handler import meeting_conversation
from commands.subte.constants import SUBTE_UPDATES_CRON
from commands.subte.updates.alerts import subte_updates_cron
from utils.utils import error_handler
from utils.constants import MINUTE

logging.basicConfig(format='%(asctime)s - %(name)30s - %(levelname)8s [%(funcName)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    # Add repeating jobs
    cron_tasks = updater.job_queue
    cron_tasks.run_repeating(subte_updates_cron,
                             interval=5 * MINUTE,
                             first=50 * MINUTE,
                             context={},
                             name=SUBTE_UPDATES_CRON)

    def load_handlers():
        commands = 0
        for folder in os.scandir('commands'):
            if folder.is_dir():
                try:
                    path = f'commands.{folder.name}.command'
                    import_module(path)
                    commands += 1
                except ImportError:
                    logger.error(f'Error importing {folder.name}')

        logger.info(f'Imported {commands} commands')

    load_handlers()

    #  Associate commands with action.
    elbot.add_handler(feedback_receiver)

    # Add callback handlers
    elbot.add_handler(serie_callback)
    elbot.add_handler(yts_callback_handler)
    elbot.add_handler(peliculas_callback)

    # Add Conversation handler
    elbot.add_handler(msup_conversation)
    elbot.add_handler(meeting_conversation)

    # Add generics
    elbot.add_handler(callback_handler)

    # Add error handler
    elbot.add_error_handler(error_handler)

    updater.start_polling()
    logger.info('Listening humans as %s..' % updater.bot.username)
    updater.idle()
    logger.info('Bot stopped gracefully')


if __name__ == '__main__':
    main()
