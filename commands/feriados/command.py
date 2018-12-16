import datetime
import logging

from commands.feriados.utils import get_feriados, prettify_feriados, filter_feriados

logger = logging.getLogger(__name__)


def feriadosarg(bot, update):
    today = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-3)))
    feriados = get_feriados(today.year)
    if not feriados:
        update.message.reply_text('🏳️ La api de feriados no responde')
        return

    following_feriados = filter_feriados(today, feriados)
    if following_feriados:
        msg = prettify_feriados(today, following_feriados)
    else:
        msg = 'No hay más feriados este año'

    update.message.reply_text(msg, parse_mode='markdown')
