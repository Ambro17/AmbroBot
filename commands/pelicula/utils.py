import os
from collections import namedtuple

import requests
import logging

from babelfish import Language
from subliminal import download_best_subtitles, save_subtitles, Movie
from subliminal.subtitle import get_subtitle_path

from commands.pelicula.constants import SUBS_DIR
from commands.serie.utils import rating_stars
from utils.constants import YT_LINK

logger = logging.getLogger(__name__)

Pelicula = namedtuple(
    'Pelicula', ['title', 'original_title', 'rating', 'overview', 'year', 'image']
)


def request_movie(pelicula_query):
    params = {
        'api_key': os.environ['TMDB_KEY'],
        'query': pelicula_query,
        'language': 'es-AR',
    }
    r = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    if r.status_code == 200:
        try:
            return r.json()['results'][0]
        except (IndexError, KeyError):
            return None


def get_basic_info(movie):
    title = movie['title']
    original_title = movie.get('original_title')
    rating = movie['vote_average']
    overview = movie['overview']
    year = movie['release_date'].split('-')[0]  # "2016-07-27" -> 2016
    image_link = movie['backdrop_path']
    poster = f"http://image.tmdb.org/t/p/original{image_link}" if image_link else None
    return Pelicula(title, original_title, rating, overview, year, poster)


def prettify_basic_movie_info(peli, with_overview=True):
    stars = rating_stars(peli.rating)
    overview = peli.overview if with_overview else ''
    title = _title_header(peli)
    return (
               f"{title}"
               f"{stars}\n\n"
               f"{overview}"
           ), peli.image

def _title_header(peli):
    if peli.original_title:
        return f"{peli.title} ({peli.original_title}) ~ {peli.year}\n"
    else:
        return f"{peli.title} ({peli.year})\n"


def get_yt_trailer(videos):
    try:
        key = videos['results'][-1]['key']
    except (KeyError, IndexError):
        return None

    return YT_LINK.format(key)


def get_yts_torrent_info(imdb_id):
    yts_api = 'https://yts.am/api/v2/list_movies.json'
    try:
        r = requests.get(yts_api, params={"query_term": imdb_id})
    except requests.exceptions.ConnectionError:
        logger.info("yts api no responde.")
        return None
    if r.status_code == 200:
        torrent = r.json()  # Dar url en lugar de hash.
        try:
            movie = torrent["data"]["movies"][0]['torrents'][0]
            url = movie['url']
            seeds = movie['seeds']
            size = movie['size']
            quality = movie['quality']

            return url, seeds, size, quality

        except (IndexError, KeyError):
            logger.exception("There was a problem with yts api response")
            return None


def search_movie_subtitle(serie_episode):
    video = Movie.fromname(serie_episode)
    subtitles = download_best_subtitles({video}, {Language('spa')})

    try:
        best_sub = subtitles[video][0]
    except IndexError:
        logger.info("No subs found for %s. Subs", serie_episode, subtitles)
        return None

    saved_subs = save_subtitles(video, [best_sub], directory=SUBS_DIR)
    if saved_subs:
        sub_filename = get_subtitle_path(video.name, language=Language('spa'))
        return os.path.join(SUBS_DIR, sub_filename)
    else:
        return None


def send_subtitle(bot, update, sub, loading_message, title):
    """Reply with the subtitle if found, else send error message"""
    chat_id = update.callback_query.message.chat_id
    if sub is None:
        logger.info("No subtitle found for the movie")
        bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
        update.effective_message.reply_text(
            f'No encontré subs para `{title}`', parse_mode='markdown'
        )

    bot.delete_message(chat_id=chat_id, message_id=loading_message.message_id)
    logger.info("Deleted loading message")
    bot.send_document(
        chat_id=chat_id,
        document=open(sub, 'rb')
    )
    logger.info("Subtitle file sent")
