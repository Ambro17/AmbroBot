import re
from collections import namedtuple
from operator import attrgetter

from telegram.ext import run_async

from updater import elbot
from utils.decorators import send_typing_action
from utils.utils import soupify_url, monospace, send_message_to_admin

Cotizacion = namedtuple('Cotizacion', 'seller, buy, sell, updated_on')
price_pattern = re.compile(r'(.*)[+\-=]')

USAGE = monospace("""
/drdolar -h      Print this usage message
/drdolar [n]     Print the top 10/n cheapest dollar rates
/drdolar -b [n]  Print the top 10/n rates from banks
/drdolar -o [n]  Print the top 10/n rates from online agencies
/drdolar --all   Print all dollar rates from cheapest to more expensive
/drdolar --ball  Print all dollar rates from banks
/drdolar --oall  Print all dollar rates from online agencies
""".strip())


@elbot.command(command='drdolar')
@send_typing_action
@run_async
def dr_dolar(bot, update):
    args = update.message.text
    url = 'https://drdolar.com/'
    limit = 10
    if args:
        if '-h' in args:
            update.message.reply_markdown(USAGE)
            return
        url, limit = read_args(args)

    soup = soupify_url(f'{url}?sort=buy')
    try:
        rates = parse_webpage(soup)
        message = format_rates(rates, limit)
    except Exception as e:
        send_message_to_admin(bot, f'dr dolar failed {e!r}.\n```{e.__traceback__}```')
        message = "Sorry, i couldn't get the requested info. Error logs have been automatically sent to the admin."

    update.message.reply_markdown(message, quote=False)


def read_args(args):
    url = 'https://drdolar.com/'
    bank_url = 'https://drdolar.com/cotizaciones/bancos'
    online_url = 'https://drdolar.com/cotizaciones/agencias-online'

    match = re.search(r'(\d+)', args)
    limit = max(int(match.group(1)), 1) if match else 10
    if '-b' in args or '--banks' in args:
        url = bank_url
    elif '-o' in args or '--online' in args:
        url = online_url
    if '--ball' in args or '—ball' in args:
        url = bank_url
        limit = None
    elif '--oall' in args or '—oall' in args:
        url = online_url
        limit = None
    if '--all' in args or '—all' in args:
        limit = None

    return url, limit


def parse_webpage(soup):
    banks = soup.find('table', class_='ratestable').tbody.find_all('tr')
    return [
        _cotizacion_from_bank(bank)
        for bank in banks
    ]  # By default they are sorted by descending price. Sort them by ascending price.


def _cotizacion_from_bank(bank):
    cells = bank.find_all('td')
    buy_price = re.search(price_pattern, cells[1].text.strip())
    sell_price = re.search(price_pattern, cells[3].text.strip())
    return Cotizacion(
        seller=cells[0].text.strip(),
        buy=buy_price.group(1) if buy_price else 'Error',
        sell=sell_price.group(1) if sell_price else 'Error',
        updated_on=cells[4].text.strip()
    )


def format_rates(cotizaciones, limit=10):
    sorted_cots = sorted(cotizaciones, key=attrgetter('sell'))
    return monospace(
        '\n'.join(
            f'{cot.seller:<17} | {cot.buy} | {cot.sell}'
            for cot in sorted_cots[:limit]
        )
    )
