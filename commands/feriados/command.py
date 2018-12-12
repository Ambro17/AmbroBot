import logging
from datetime import datetime as d

from commands.feriados.constants import YEAR_2019, FERIADOS_URL, FERIADOS_2019_URL
from commands.feriados.utils import get_feriados, prettify_feriados
from utils.utils import soupify_url

logger = logging.getLogger(__name__)


def feriados(bot, update, **kwargs):
    year = kwargs.get('args')
    if year and year[0] == YEAR_2019:
        url = FERIADOS_2019_URL
        month = None
    else:
        url = FERIADOS_URL
        month = d.today().month

    # Set the header to trick the page to think we have javascript enabled and thus load the full page.
    header = {'Cookie': 'has_js=1'}
    soup = soupify_url(url, headers=header)
    the_feriados = get_feriados(soup)
    pretty_feriados = prettify_feriados(the_feriados, from_month=month)

    bot.send_message(chat_id=update.message.chat_id, text=pretty_feriados or 'No pude obtener los feriados')
