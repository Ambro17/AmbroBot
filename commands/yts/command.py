import logging

import requests
from telegram.ext import run_async

from commands.yts.utils import get_minimal_movie, prettify_yts_movie
from utils.decorators import send_typing_action
from keyboards.keyboards import yts_navigator_keyboard

logger = logging.getLogger(__name__)

@send_typing_action
@run_async
def yts(bot, update, chat_data):
    try:
        r = requests.get('https://yts.am/api/v2/list_movies.json', params={'limit': 50})
    except requests.exceptions.ConnectionError:
        update.message.reply_text("📡 La api de yts está caida. Intentá más tarde")
        return
    if r.status_code != 200:
        logger.info(f"Yts api down. {r.status_code}")
        return None
    try:
        movies = r.json()['data']['movies']
    except KeyError:
        logger.info(f'Response has no moives {r.url} {r.status_code} {r.reason} {r.json()}')
        return None

    # Build context based on the imdb_id
    chat_data['context'] = {
        'data': movies,
        'movie_number': 0,
        'movie_count': len(movies),
        'command': 'yts',
        'edit_original_text': True,
    }
    title, synopsis, rating, imdb, yt_trailer, image = get_minimal_movie(movies[0])
    movie_desc = prettify_yts_movie(title, synopsis, rating)
    yts_navigator = yts_navigator_keyboard(imdb_id=imdb, yt_trailer=yt_trailer)
    bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image,
        caption=movie_desc,
        reply_markup=yts_navigator
    )