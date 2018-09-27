import json
import logging
import re
import os

from lxml import etree
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

from utils import get_moneda, format_moneda_output
from telegram.ext.dispatcher import run_async


logger = logging.getLogger(__name__)

def extraer_info(partido):
    logo = partido.img.attrs['src']
    fecha = partido.find('div', {'class': 'temp'}).text
    hora, tv, estadio, arbitro =[p.text for p in partido.find_all('p') if p.text]
    return logo, fecha, hora, tv, estadio, arbitro

def soupify_url(url, timeout=2):
    """Given a url returns a BeautifulSoup object"""
    r = requests.get(url, timeout=timeout)
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'lxml')
    else:
        raise ConnectionError(f'{url} did not respond.')

@run_async
def partido(bot, update, args):
    soup = soupify_url('https://mundoazulgrana.com.ar/sanlorenzo/')
    partido = soup.find('div', {'class': 'widget-partido'}).find('div', {'class': 'cont'})
    logo, *info = extraer_info(partido)
    bot.send_photo(chat_id=update.message.chat_id, photo=logo)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='\n'.join(info)
    )


def ping(bot, update):
    FECHA_PATH = './div/table/tr[2]/td/div/strong/text()'
    CALENDAR_PATH = ('/html/body/table/tr/td/div/table/tr/td/table/tr[3]/td/'
                     'table/tr/td[2]/table/tr/td/table/tr/td/table/tr[2]/td/'
                     'table/tr[3]/td/div/table/tr/td/table/tr[2]/td[1]')
    r = requests.get('https://www.tenisdemesaparatodos.com/calendario.asp')
    html = etree.HTML(r.text)
    calendario = html.xpath(CALENDAR_PATH)[0]
    fecha = calendario.xpath(FECHA_PATH)[0]
    torneo = calendario.xpath('./div/table/tr[3]/td/table/tr/td[2]/a/strong/span/text()')[0]
    torneo2 = calendario.xpath('./div/table/tr[5]/td/table/tr/td[2]/a/strong/span/text()')[0]
    # /html/body/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/
    # td/table/tbody/tr[3]/td/div/table/tbody/tr/td/table/tbody/tr[2]/td
    bot.send_message(
        chat_id=update.message.chat_id,
        text="El próximo torneo de ping pong es el {}"
    )


def rec(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tenes que acordarte de hacer {} a las 11 y esto {} a las 12"
    )

def get_cotizaciones(response_soup):
    """Returns a dict of cotizaciones with banco as keys and exchange rate as value.

    {
        "Banco Nación": {
            "Compra": "30.00",
            "Venta": "32.00",
        },
        "Banco Galicia": {
            "Compra": "31.00",
            "Venta": "33.00",
        }
    }

    """
    cotizaciones = defaultdict(dict)
    for table in response_soup:
        # Get cotizaciones
        for row_cotizacion in table.tbody.find_all('tr'):
            banco, compra, venta = (item.get_text() for item in row_cotizacion.find_all('td'))
            banco = banco.replace('Banco ', '')
            cotizaciones[banco]['compra'] = compra
            cotizaciones[banco]['venta'] = venta

    return cotizaciones

def pretty_print_dolar(cotizaciones):
    """Returns dolar rates separated by newlines and with code markdown syntax.
    ```
    Banco Nacion  | $30.00 | $40.00
    Banco Galicia | $30.00 | $40.00
                   ...
    ```
    """
    MONOSPACE = "```\n{}\n```"
    return MONOSPACE.format('\n'.join(
            "{:8} | {:7} | {:7}".format(normalize(banco, limit=7), valor['compra'], valor['venta'])
            for banco, valor in cotizaciones.items()
        ))

@run_async
def dolar_hoy(bot, update):
    soup = soupify_url("http://www.dolarhoy.com/usd")
    data = soup.find_all('table')

    cotiz = get_cotizaciones(data)
    pretty_result = pretty_print_dolar(cotiz)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=pretty_result,
        parse_mode='markdown'
    )

def meme(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="En un futuro voy a entender que me pases un identificador y una imagen y despues voy a reenviarla dado "
             "ese identificador")

@run_async
def default(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="No sé qué decirte..")

@run_async
def dolar_futuro(bot, update):
    url = 'http://www.ambito.com/economia/mercados/indices/rofex/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    rofex_table = soup.find("table", {"id": "rofextable"})

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

    def conditional_format(a, b, c):
        """Prepends a $ if str is a number"""
        b = f'$ {b}' if re.match(r'^\d+', b) else b
        c = f'$ {c}' if re.match(r'^\d+', c) else c
        return "{:16} | {:7} | {:7}".format(a,b,c)

    def prettify_rofex(rofex_vals):
        MONOSPACE = "```\n{}\n```"
        return MONOSPACE.format('\n'.join(
            conditional_format(a,b,c)
            for a, b, c in rofex_vals
        ))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=prettify_rofex(get_rofex()),
        parse_mode='markdown'
    )

def normalize(text, limit=11):
    """Trim and append . if text is too long. Else return it unmodified"""
    return f'{text[:limit]}.' if len(text) > limit else text

def parse_posiciones(tabla, posiciones=None):
    # #, Equipo, pts y PJ
    posiciones = int(posiciones[0]) if posiciones else 5
    logger.info(f'received argument {posiciones}')
    logger.info(f'raw_table={tabla}')
    LIMIT = 4
    headers = [th.text for th in tabla.thead.find_all('th')[:LIMIT]]
    res = [
        [normalize(r.text) for r in row.find_all('td')[:LIMIT]]
        for row in
        tabla.tbody.find_all('tr')[:posiciones]]
    res.insert(0, headers)
    return res

def monospace(text):
    return f'```\n{text}\n```'

def prettify_table(info):
    try:
        return monospace('\n'.join(
            '{:2} | {:12} | {:3} | {:3}'.format(*team_stat) for
            team_stat in info
        ))
    except Exception:
        logger.error(f"Error Prettying info {info}")
        return 'No te entiendo..'

@run_async
def posiciones(bot, update, **kwargs):
    soup = soupify_url('http://www.promiedos.com.ar/primera')
    tabla = soup.find('table', {'id': 'posiciones'})
    info = parse_posiciones(tabla, posiciones=kwargs.get('args'))
    pretty = prettify_table(info)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=pretty,
        parse_mode='markdown'
    )

@run_async
def link_ticket(bot, update, **kwargs):
    ticket_id = kwargs.get('groupdict').get('ticket')
    if ticket_id:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=os.environ['jira'].format(ticket_id)
        )


@run_async
def format_code(bot, update, **kwargs):
    code = kwargs.get('groupdict').get('code')
    if code:
        reply_markdown(code, bot, update)

def reply_markdown(message, bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=monospace(message),
        parse_mode='markdown'
    )

def subte(bot, update):
    # kwarg can be a b c.
    soup = soupify_url('https://www.metrovias.com.ar/')
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
        text=monospace('\n'.join(
            format_estado_de_linea(info_de_linea)
            for info_de_linea in estado_lineas
        )),
        parse_mode='markdown'
    )

@run_async
def format_estado_de_linea(info_de_linea):
    linea, estado = info_de_linea
    if estado.lower() == 'normal':
        estado = '✅'
    else:
        estado = f'⚠ {estado} ⚠'
    return f'{linea} {estado}'

