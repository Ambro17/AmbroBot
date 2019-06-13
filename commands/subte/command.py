import logging

from telegram.ext import run_async, CommandHandler

from commands.subte.constants import SUBTE_UPDATES_CRON, SUBWAY_STATUS_OK
from commands.subte.updates.alerts import check_update
from commands.subte.updates.utils import prettify_updates
from updater import elbot
from utils.constants import MINUTE
from utils.decorators import send_typing_action, log_time, admin_only, handle_empty_arg

logger = logging.getLogger(__name__)


@elbot.command(command='subte')
@log_time
@send_typing_action
@run_async
def subte(bot, update):
    """Estado de las lineas de subte, premetro y urquiza."""
    NO_PROBLEMS = {}
    try:
        updates = check_update()
    except Exception:
        msg = 'Error checking updates. You can check status here https://www.metrovias.com.ar/'
        update.message.reply_text(msg)
        return

    if updates is None:
        msg = 'API did not respond with status 200,\n. You can check subte status here https://www.metrovias.com.ar/'
    elif updates == NO_PROBLEMS:
        msg = SUBWAY_STATUS_OK
    else:
        msg = prettify_updates(updates)

    update.message.reply_text(msg)


@elbot.command(command='setsubfreq', pass_job_queue=True, pass_args=True)
@admin_only
@handle_empty_arg(required_params=('args',), error_message='Missing required frequency to set for the updates')
def modify_freq(bot, update, job_queue, args):
    """Modify subte updates cron tu run every x minutes"""
    minutes = args[0]
    subte_cron = job_queue.get_jobs_by_name(SUBTE_UPDATES_CRON)
    try:
        minute_seconds = float(minutes) * MINUTE
        subte_cron[0].interval = minute_seconds
        msg = f'Subte updates cron frequency set to {minutes} minutes. Seconds ({minute_seconds})'
    except ValueError:
        msg = f'Frequency must be an int or a float.'
    except IndexError:
        msg = f'No job found with name {SUBTE_UPDATES_CRON}'

    update.message.reply_text(msg)
    logger.info(msg)
