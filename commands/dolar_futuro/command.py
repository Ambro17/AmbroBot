from telegram.ext import run_async

from commands.dolar_futuro.constants import DOLAR_REGEX, Contrato, month_name
from utils.decorators import send_typing_action, log_time
from utils.command_utils import soupify_url, monospace


@send_typing_action
@run_async
@log_time
def rofex(bot, update):
    """Print dolar futuro contracts."""
    contratos = prettify_rofex(get_rofex())
    update.message.reply_text(contratos, parse_mode='markdown')


def get_rofex():
    soup = soupify_url('http://www.rofex.com.ar/')
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
    return monospace(header + values)
