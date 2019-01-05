import re
import logging

from requests.exceptions import ReadTimeout
from telegram.ext import run_async

from commands.subte.constants import SUBTE_UPDATES_CRON
from commands.subte.utils import format_estado_de_linea
from utils.constants import MINUTE
from utils.decorators import send_typing_action, log_time, admin_only, handle_empty_arg
from utils.utils import soupify_url, monospace

logger = logging.getLogger(__name__)


@log_time
@send_typing_action
@run_async
def subte(bot, update):
    """Estado de las lineas de subte, premetro y urquiza."""
    try:
        soup = soupify_url('https://www.metrovias.com.ar')
    except ReadTimeout:
        logger.info('Error in metrovias url request')
        update.message.reply_text('⚠️ Metrovias no responde. Intentá más tarde')
        return

    subtes = soup.find('table', {'class': 'table'})
    REGEX = re.compile(r'Línea *([A-Z]){1} +(.*)', re.IGNORECASE)
    estado_lineas = []
    for tr in subtes.tbody.find_all('tr'):
        estado_linea = tr.text.strip().replace('\n', ' ')
        match = REGEX.search(estado_linea)
        if match:
            linea, estado = match.groups()
            estado_lineas.append((linea, estado))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=monospace(
            '\n'.join(
                format_estado_de_linea(info_de_linea) for info_de_linea in estado_lineas
            )
        ),
        parse_mode='markdown',
    )


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
