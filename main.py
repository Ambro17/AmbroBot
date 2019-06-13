import glob
import logging
import os
from importlib import import_module

from telegram.ext import Updater

from updater import elbot

from callbacks.handler import callback_handler
from commands.aproximacion.command import msup_conversation
from commands.feedback.command import feedback_receiver
from commands.meeting.conversation_handler import meeting_conversation
from commands.subte.constants import SUBTE_UPDATES_CRON
from commands.subte.updates.alerts import subte_updates_cron
from utils.utils import error_handler, unknown_commands, signal_handler
from utils.constants import MINUTE

logging.basicConfig(format='%(asctime)s - %(name)30s - %(levelname)8s [%(funcName)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    # Add repeating jobs
    updater = Updater(os.environ['PYTEL'], user_sig_handler=signal_handler)
    dp = updater.dispatcher
    cron_tasks = updater.job_queue
    cron_tasks.run_repeating(subte_updates_cron,
                             interval=5 * MINUTE,
                             first=50 * MINUTE,
                             context={},
                             name=SUBTE_UPDATES_CRON)

    def import_commands():
        """Load all decorated callbacks from commands subdirectory"""
        commands = []
        callbacks = []
        for command_file in glob.glob('commands/**/command.py', recursive=True):
            try:
                import_path = command_file.replace('/', '.').rstrip('.py')  # 'my_path/to_file.py' -> 'my_path.to_file'
                import_module(import_path)
                commands.append(import_path)
            except ImportError:
                logger.error(f'Error importing {import_path}')

        for callback_file in glob.glob('commands/**/callback.py', recursive=True):
            try:
                import_path = callback_file.replace('/', '.').rstrip('.py')
                import_module(import_path)
                callbacks.append(import_path)
            except ImportError:
                logger.error(f'Error importing {import_path}')

        logger.info(f'Imported {len(commands)} commands:\n{sorted(commands)}')
        logger.info(f'Imported {len(callbacks)} callbacks:\n{sorted(callbacks)}')

    import_commands()

    def add_handlers(updater, elbot):
        for handler_desc in elbot.handlers:
            handler, group = handler_desc['handler'], handler_desc['group']
            updater.dispatcher.add_handler(handler, group)

    add_handlers(updater, elbot)

    # Add Conversation handlers
    dp.add_handler(feedback_receiver)
    dp.add_handler(msup_conversation)
    dp.add_handler(meeting_conversation)

    # Add fallback handlers for unhandled commands and callbacks,
    dp.add_handler(callback_handler)
    dp.add_handler(unknown_commands)

    # Add error handler
    dp.add_error_handler(error_handler)

    # Start listening
    updater.start_polling()
    logger.info('Listening humans as %s..' % updater.bot.username)
    updater.idle()

    logger.info('Bot stopped gracefully')


if __name__ == '__main__':
    main()
