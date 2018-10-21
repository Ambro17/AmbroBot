# -*- coding: utf-8 -*-
import logging
import re
import os

import requests
from telegram.ext.dispatcher import run_async

from command.hoypido.hoypido import get_comidas, prettify_food_offers
from command.movies.movie_utils import get_movie, prettify_movie
from command.serie.utils import prettify_serie, get_all_seasons
from decorators import send_typing_action, log_time
from keyboards.keyboards import banco_keyboard, pelis_keyboard, hoypido_keyboard, serie_keyboard
from utils.command_utils import (
    monospace,
    soupify_url,
    get_cotizaciones,
    pretty_print_dolar,
    info_de_partido,
    parse_posiciones,
    prettify_table_posiciones,
    format_estado_de_linea,
)

logger = logging.getLogger(__name__)


# ------------- PARTIDO -----------------
@send_typing_action
@run_async
@log_time
def partido(bot, update):
    soup = soupify_url('https://mundoazulgrana.com.ar/sanlorenzo/')
    partido = soup.find('div', {'class': 'widget-partido'}).find(
        'div', {'class': 'cont'}
    )
    logo, *info = info_de_partido(partido)
    bot.send_photo(chat_id=update.message.chat_id, photo=logo)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(info))


# ------------- DOLAR_HOY -----------------
@send_typing_action
@run_async
@log_time
def dolar_hoy(bot, update, chat_data):
    soup = soupify_url("http://www.dolarhoy.com/usd")
    data = soup.find_all('table')

    cotiz = get_cotizaciones(data)
    pretty_result = pretty_print_dolar(cotiz)

    chat_data['context'] = {
        'data': cotiz,
        'command': 'dolarhoy',
        'edit_original_text': True
    }
    keyboard = banco_keyboard()
    bot.send_message(
        update.message.chat_id,
        text=pretty_result,
        reply_markup=keyboard,
        parse_mode='markdown',
    )


# ------------- DOLAR_FUTURO -----------------
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


# ------------- POSICIONES -----------------
@send_typing_action
@run_async
@log_time
def posiciones(bot, update, **kwargs):
    soup = soupify_url('http://www.promiedos.com.ar/primera')
    tabla = soup.find('table', {'id': 'posiciones'})
    info = parse_posiciones(tabla, posiciones=kwargs.get('args'))
    pretty = prettify_table_posiciones(info)
    bot.send_message(chat_id=update.message.chat_id, text=pretty, parse_mode='markdown')


# ------------- FORMAT_CODE -----------------
@send_typing_action
@run_async
def format_code(bot, update, **kwargs):
    """Format text as code if it starts with $, ~, \c or \code."""
    code = kwargs.get('groupdict').get('code')
    if code:
        bot.send_message(
            chat_id=update.message.chat_id, text=monospace(code), parse_mode='markdown'
        )


# ------------- SUBTE -----------------
@send_typing_action
@run_async
@log_time
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
        text=monospace(
            '\n'.join(
                format_estado_de_linea(info_de_linea) for info_de_linea in estado_lineas
            )
        ),
        parse_mode='markdown',
    )


# ------------- CARTELERA -----------------
@send_typing_action
@run_async
@log_time
def cinearg(bot, update):
    """Get top 5 Argentina movies"""
    CINE_URL = 'https://www.cinesargentinos.com.ar/cartelera'
    soup = soupify_url(CINE_URL)
    cartelera = soup.find('div', {'class': 'contenidoRankingContainer'})
    listado = [
        (rank, li.text, CINE_URL + li.a['href'])
        for rank, li in enumerate(cartelera.div.ol.find_all('li'), 1)
    ]
    top_5 = '\n'.join(f'[{rank}. {title}]({link})' for rank, title, link in listado[:5])
    bot.send_message(chat_id=update.message.chat_id, text=top_5, parse_mode='markdown')


# ------------- BUSCAR_PELICULA -----------------
@send_typing_action
@run_async
@log_time
def buscar_peli(bot, update, chat_data, **kwargs):
    pelicula = kwargs.get('args')
    if not pelicula:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Necesito que me pases una pelicula. /pelicula <nombre>',
        )
        return

    try:
        pelicula_query = ' '.join(pelicula)
        movie = get_movie(pelicula_query)
        if not movie:
            bot.send_message(
                chat_id=update.message.chat_id,
                text='No encontré info sobre %s' % pelicula_query,
            )
            return

        # Give context to button handlers
        chat_data['context'] = {
            'data': dict(movie=movie['id'], title=movie['title']),
            'command': 'pelicula',
            'edit_original_text': False,
        }

        movie_details = prettify_movie(movie)  # Add photo to basic output
        #movie_details = search_movie(pelicula)
        keyboard = pelis_keyboard()
        bot.send_message(
            chat_id=update.message.chat_id,
            text=movie_details,
            reply_markup=keyboard,
            parse_mode='markdown',
            disable_web_page_preview=True,
        )
    except requests.exceptions.ConnectionError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Estoy descansando ahora, probá después de la siesta',
            parse_mode='markdown',
        )
    # Add photo


# ------------- DEFAULT -----------------
@send_typing_action
@run_async
def default(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    bot.send_message(chat_id=update.message.chat_id, text="No sé qué decirte..")


# ------------- LINK_TICKET -----------------
@send_typing_action
@run_async
def link_ticket(bot, update, **kwargs):
    """Given a ticket id, return the url."""
    ticket_id = kwargs.get('groupdict').get('ticket')
    if ticket_id:
        bot.send_message(
            chat_id=update.message.chat_id, text=os.environ['jira'].format(ticket_id)
        )


# ------------- HOYPIDO -----------------
@send_typing_action
@run_async
def hoypido(bot, update, chat_data):
    comidas = get_comidas()
    pretty_comidas = prettify_food_offers(comidas)

    chat_data['context'] = {
        'data': comidas,
        'command': 'hoypido',
        'edit_original_text': True
    }

    keyboard = hoypido_keyboard()
    bot.send_message(
        update.message.chat_id,
        text=pretty_comidas,
        reply_markup=keyboard,
        parse_mode='markdown',
    )

# ------------- SERIE -----------------
@send_typing_action
@run_async
def serie(bot, update, chat_data, **kwargs):
    serie = kwargs.get('args')
    if not serie:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Te faltó pasarme el nombre de la serie. /serie <serie>',
        )
        return

    # Obtener id de imdb
    serie = ' '.join(serie)
    params = {'api_key': os.environ['TMDB_KEY'], 'query': serie}
    r = requests.get('https://api.themoviedb.org/3/search/tv', params=params)
    if r.status_code != 200:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"No encontré información en imdb sobre '{serie}'. Está bien escrito el nombre?",
        )
        return

    try:
        serie = r.json()['results'][0]
    except (KeyError, IndexError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"No encontré resultados en imdb sobre '{serie}'",
        )
        return

    # Send basic info to user
    serie_id = serie['id']
    name = serie['name']
    start_date = serie.get('first_air_date').split('-')[0] if serie['first_air_date'] else '' # 2014-12-28 -> 2014 or ''
    rating = serie['vote_average']
    overview = serie['overview']
    image = f"http://image.tmdb.org/t/p/original{serie['backdrop_path']}"
    response = prettify_serie(name, rating, overview, start_date)

    # We reply here with basic info because further info may take a while to process.
    bot.send_photo(update.message.chat_id, image)
    bot_reply = bot.send_message(
        chat_id=update.message.chat_id,
        text=response,
        parse_mode='markdown'
    )

    # Retrieve imdb_id for further requests on button callbacks
    params.pop('query')
    r_id = requests.get(f'https://api.themoviedb.org/3/tv/{serie_id}/external_ids', params=params)
    if r_id.status_code != 200:
        logger.info(f"Request for imdb id was not succesfull. {r_id.reason} {r_id.status_code} {r_id.url}")
        bot.send_message(
            chat_id=update.message.chat_id,
            text='La api de imdb se puso la gorra 👮',
            parse_mode='markdown'
        )
        return

    try:
        imdb_id = r_id.json()['imdb_id'].replace('t', '')  # tt<id> -> <id>
    except KeyError:
        logger.info("imdb id for the movie not found")
        bot.send_message(
            chat_id=update.message.chat_id,
            text='No encontré el id de imdb de esta pelicula',
            parse_mode='markdown'
        )
        return

    # Build context based on the imdb_id
    chat_data['context'] = {
        'data': {'imdb_id': imdb_id, 'series_name': name, 'message_info': (name, rating, overview, start_date)},
        'command': 'serie',
        'edit_original_text': True,
    }

    # Now that i have the imdb_id, show buttons to retrieve extra info.
    keyboard = serie_keyboard()
    bot.edit_message_reply_markup(
        chat_id=bot_reply.chat_id,
        message_id=bot_reply.message_id,
        text=bot_reply.caption,
        reply_markup=keyboard,
        parse_mode='markdown',
        disable_web_page_preview=True,
    )
    logger.info("Retrieving all seasons to gain time")
    all_seasons = get_all_seasons(name)
    logger.info("All seasons data retrieved")
    chat_data['context']['seasons'] = all_seasons