import os
from collections import namedtuple

import requests
import logging

from commands.serie.utils import rating_stars
from utils.constants import YT_LINK

logger = logging.getLogger(__name__)

Pelicula = namedtuple('Pelicula', ['title', 'rating', 'overview', 'year', 'image'])


def request_movie(pelicula_query):
    params = {'api_key': os.environ['TMDB_KEY'], 'query': pelicula_query, 'language': 'es-AR'}
    r = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    if r.status_code == 200:
        try:
            return r.json()['results'][0]
        except (IndexError, KeyError):
            return None


def get_basic_info(movie):
    title = movie['title']
    rating = movie['vote_average']
    overview = movie['overview']
    year = movie['release_date'].split('-')[0]  # "2016-07-27" -> 2016
    image_link = movie['backdrop_path']
    poster = f"http://image.tmdb.org/t/p/original{image_link}" if image_link else None
    return Pelicula(title, rating, overview, year, poster)


def prettify_basic_movie_info(pelicula, with_overview=True):
    stars = rating_stars(pelicula.rating)
    overview = f"{pelicula.overview}\n\n" if with_overview else ''
    return (
               f"{pelicula.title} ({pelicula.year})\n"
               f"{stars}\n\n"
               f"{overview}"
           ), pelicula.image


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

        except (IndexError, KeyError) as e:
            logger.exception("There was a problem with yts api response")
            return None
