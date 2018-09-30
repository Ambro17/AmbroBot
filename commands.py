import json
import logging
import re
import os

import telegram
from lxml import etree
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

from telegram import MessageEntity
from telegram.ext.dispatcher import run_async

from decorators import send_typing_action
from utils.command_utils import monospace, soupify_url, get_cotizaciones, pretty_print_dolar, info_de_partido, \
    parse_posiciones, prettify_table_posiciones, format_estado_de_linea

logger = logging.getLogger(__name__)


# ------------- PARTIDO -----------------
@run_async
def partido(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
    soup = soupify_url('https://mundoazulgrana.com.ar/sanlorenzo/')
    partido = soup.find('div', {'class': 'widget-partido'}).find('div', {'class': 'cont'})
    logo, *info = info_de_partido(partido)
    bot.send_photo(chat_id=update.message.chat_id, photo=logo)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='\n'.join(info)
    )


# ------------- DOLAR_HOY -----------------
@send_typing_action
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


# ------------- LINK_TICKET -----------------
@send_typing_action
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


# ------------- POSICIONES -----------------
@send_typing_action
@run_async
def posiciones(bot, update, **kwargs):
    soup = soupify_url('http://www.promiedos.com.ar/primera')
    tabla = soup.find('table', {'id': 'posiciones'})
    info = parse_posiciones(tabla, posiciones=kwargs.get('args'))
    pretty = prettify_table_posiciones(info)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=pretty,
        parse_mode='markdown'
    )


# ------------- LINK_TICKET -----------------
@send_typing_action
@run_async
def link_ticket(bot, update, **kwargs):
    """Given a ticket id, return the url."""
    ticket_id = kwargs.get('groupdict').get('ticket')
    if ticket_id:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=os.environ['jira'].format(ticket_id)
        )


# ------------- FORMAT_CODE -----------------
@send_typing_action
@run_async
def format_code(bot, update, **kwargs):
    """Format text as code if it starts with $, ~, \c or \code."""
    code = kwargs.get('groupdict').get('code')
    if code:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=monospace(code),
            parse_mode='markdown'
        )


# ------------- SUBTE -----------------
@send_typing_action
@run_async
def subte(bot, update):
    """Estado de las lineas de subte, premetro y urquiza."""
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


# ------------- CARTELERA -----------------
@send_typing_action
@run_async
def cartelera(bot, update):
    """Get top 5 Argentina movies"""
    CINE_URL = 'https://www.cinesargentinos.com.ar/cartelera'
    soup = soupify_url(CINE_URL)
    cartelera = soup.find('div', {'class': 'contenidoRankingContainer'})
    listado = [
        (rank, li.text, CINE_URL+li.a['href'])
        for rank, li in
        enumerate(cartelera.div.ol.find_all('li'), 1)]
    top_5 = '\n'.join(
        f'[{rank}. {title}]({link})' for rank, title, link
        in listado[:5]
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text=top_5,
        parse_mode='markdown'
    )


# ------------- DEFAULT -----------------
@send_typing_action
@run_async
def default(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    bot.send_message(
        chat_id=update.message.chat_id,
        text="No sé qué decirte..")

# to be implemented
def rec(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Tenes que acordarte de hacer {} a las 11 y esto {} a las 12"
    )
