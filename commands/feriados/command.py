from datetime import datetime as d

from commands.feriados.constants import YEAR_2019, FERIADOS_URL, FERIADOS_2019_URL
from commands.feriados.utils import get_feriados, prettify_feriados
from utils.command_utils import soupify_url


def feriados(bot, update, **kwargs):
    year = kwargs.get('args')
    if year and year[0] == YEAR_2019:
        url = FERIADOS_2019_URL
        month = None
    else:
        url = FERIADOS_URL
        month = d.today().month

    soup = soupify_url(url)
    feriados = get_feriados(soup)
    pretty_feriados = prettify_feriados(feriados, from_month=month)

    bot.send_message(chat_id=update.message.chat_id, text=pretty_feriados)


