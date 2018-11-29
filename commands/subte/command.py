import re
import logging

from requests.exceptions import ReadTimeout
from telegram.ext import run_async

from commands.subte.utils import format_estado_de_linea
from utils.decorators import send_typing_action, log_time
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
