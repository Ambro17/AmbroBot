from telegram.ext import run_async

from commands.dolar_futuro.constants import DOLAR_REGEX, Contrato, month_name, EMPTY_MESSAGE
from utils.decorators import send_typing_action, log_time
from utils.utils import soupify_url, monospace


@log_time
@send_typing_action
@run_async
def rofex(bot, update):
    """Print dolar futuro contracts."""
    rofex_data = get_rofex()
    contratos = prettify_rofex(rofex_data)
    update.message.reply_text(contratos, parse_mode='markdown')


def get_rofex():
    try:
        soup = soupify_url('http://www.rofex.com.ar/')
    except TimeoutError:
        return None

    table = soup.find('table', class_='table-rofex')
    cotizaciones = table.find_all('tr')[1:]  # Exclude header
    contratos = []

    for cotizacion in cotizaciones:
        contrato, valor, _, variacion, var_porc = cotizacion.find_all('td')
        month, year = DOLAR_REGEX.match(contrato.text).groups()
        contratos.append(Contrato(int(month), year, valor.text))

    return contratos


def prettify_rofex(contratos):
    values = '\n'.join(
        f"{month_name[month]} {year} | {value[:5]}" for month, year, value in contratos
    )
    header = '  Dólar  | Valor\n'
    return monospace(header + values) if contratos is not None else EMPTY_MESSAGE
