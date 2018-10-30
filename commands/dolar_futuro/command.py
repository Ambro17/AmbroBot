import re

from telegram.ext import run_async

from utils.decorators import send_typing_action, log_time
from utils.command_utils import soupify_url, monospace


@send_typing_action
@run_async
@log_time
def dolar_futuro(bot, update):
    soup = soupify_url('http://www.ambito.com/economia/mercados/indices/rofex/')
    rofex_table = soup.find("table", {"id": "rofextable"})
    NUMBER = re.compile(r'^\d+')

    def get_rofex():
        rofex = []
        # Get headers
        headers = [th.text for th in rofex_table.thead.tr.find_all('th')]
        rofex.append(headers)
        # Get values
        for row in rofex_table.find_all('tr')[1:]:
            contrato, compra, venta = extract_values(row)
            if not empty(compra, venta):
                rofex.append((contrato, compra, venta))
        return rofex

    def extract_values(row):
        tds = [td.text for td in row.find_all('td')]
        # Replace Dollar and double space.
        contrato = row.th.text.strip().replace('  ', ' ').replace('Dólar ', '')
        return contrato, tds[0], tds[1]

    def empty(val, val2):
        return val == '-' or val2 == '-'

    def compact_contrato(contrato):
        """Reduces length of str to make it more compact.

        Turns Octubre 2018 into Oct. '18,
              Noviembre 2018 into Nov. '18
        """
        try:
            mes, año = contrato.split()
        except ValueError:
            # Return it unmodified
            return contrato

        return f"{mes[:3]}. '{año[-2:]}"

    def conditional_format(contrato, compra, venta):
        """Prepends a $ if str is a number"""
        contrato = compact_contrato(contrato)
        compra = f'$ {compra[:5]}' if NUMBER.match(compra) else compra
        venta = f'$ {venta[:5]}' if NUMBER.match(venta) else venta
        return "{:8} | {:7} | {:7}".format(contrato, compra, venta)

    def prettify_rofex(rofex_vals):
        return monospace(
            '\n'.join(conditional_format(a, b, c) for a, b, c in rofex_vals)
        )

    bot.send_message(
        chat_id=update.message.chat_id,
        text=prettify_rofex(get_rofex()),
        parse_mode='markdown',
    )
