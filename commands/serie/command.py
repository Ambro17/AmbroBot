import logging
import os

import requests
from telegram.ext import run_async, CommandHandler

from commands.serie.keyboard import serie_main_keyboard
from commands.serie.utils import prettify_serie
from updater import elbot
from utils.decorators import send_typing_action, log_time

logger = logging.getLogger(__name__)


@log_time
@send_typing_action
@run_async
@elbot.route(command='serie', pass_chat_data=True, pass_args=True)
def serie(bot, update, chat_data, args):
    if not args:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Te faltó pasarme el nombre de la serie. `/serie <serie>`',
            parse_mode='markdown',
        )
        return

    # Obtener id de imdb
    serie_query = ' '.join(args)
    params = {'api_key': os.environ['TMDB_KEY'], 'query': serie_query}
    r = requests.get('https://api.themoviedb.org/3/search/tv', params=params)
    if r.status_code != 200:
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"No encontré información en imdb sobre '{serie_query}'. Está bien escrito el nombre?",
        )
        return

    try:
        serie = r.json()['results'][0]
    except (KeyError, IndexError):
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"No encontré resultados en imdb sobre '{serie_query}'",
        )
        return

    # Send basic info to user
    serie_id = serie['id']
    name = serie['name']
    start_date = serie.get('first_air_date').split('-')[0] if serie['first_air_date'] else ''  # 2014-12-28-> 2014 or ''
    rating = serie['vote_average']
    overview = serie['overview']
    image = f"http://image.tmdb.org/t/p/original{serie['backdrop_path']}"
    response = prettify_serie(name, rating, overview, start_date)

    # We reply here with basic info because further info may take a while to process.
    bot.send_photo(update.message.chat_id, image)
    bot_reply = bot.send_message(
        chat_id=update.message.chat_id, text=response, parse_mode='markdown'
    )

    # Retrieve imdb_id for further requests on button callbacks
    params.pop('query')
    r_id = requests.get(
        f'https://api.themoviedb.org/3/tv/{serie_id}/external_ids', params=params
    )
    if r_id.status_code != 200:
        logger.info(
            f"Request for imdb id was not succesfull. {r_id.reason} {r_id.status_code} {r_id.url}"
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text='La api de imdb se puso la gorra 👮',
            parse_mode='markdown',
        )
        return

    try:
        imdb_id = r_id.json()['imdb_id'].replace('t', '')  # tt<id> -> <id>
    except KeyError:
        logger.info("imdb id for the movie not found")
        bot.send_message(
            chat_id=update.message.chat_id,
            text='No encontré el id de imdb de esta pelicula',
            parse_mode='markdown',
        )
        return

    # Build context based on the imdb_id
    chat_data['context'] = {
        'data': {
            'imdb_id': imdb_id,
            'series_name': name,
            'series_raw_name': serie_query,
            'message_info': (name, rating, overview, start_date),
        },
    }

    # Now that i have the imdb_id, show buttons to retrieve extra info.
    keyboard = serie_main_keyboard(imdb_id)
    bot.edit_message_reply_markup(
        chat_id=bot_reply.chat_id,
        message_id=bot_reply.message_id,
        text=bot_reply.caption,
        reply_markup=keyboard,
        parse_mode='markdown',
        disable_web_page_preview=True,
    )
