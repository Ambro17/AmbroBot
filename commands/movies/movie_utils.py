import requests
import logging

from commands.serie.utils import rating_stars
from utils.constants import YT_LINK

TMDB_KEY = '7f76943e1557e33276e0f595c2128f68'
logger = logging.getLogger(__name__)


def get_movie(pelicula_query):
    params = {'api_key': TMDB_KEY, 'query': pelicula_query, 'language': 'es-AR'}
    r = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    if r.status_code == 200:
        try:
            return r.json()['results'][0]
        except (IndexError, KeyError):
            return None


def prettify_movie(movie_dict):
    movie_info = get_basic_info(movie_dict)
    message, image = prettify_basic_movie_info(*movie_info)

    return message, image


def get_basic_info(movie):
    title = movie['title']
    rating = movie['vote_average']
    overview = movie['overview']
    year = movie['release_date'].split('-')[0]  # "2016-07-27" -> 2016
    image = f"http://image.tmdb.org/t/p/original{movie['backdrop_path']}"
    return title, rating, overview, year, image


def prettify_basic_movie_info(title, rating, overview, year, image):
    stars = rating_stars(rating)
    return (
        f"{title} ({year})\n"
        f"{stars}\n\n"
        f"{overview}\n\n"
    ), image


def get_yt_trailer(videos):
    key = videos['results'][-1]['key']
    return YT_LINK.format(key)


def get_torrent_info(imdb_id):
    yts_api = 'https://yts.am/api/v2/list_movies.json'
    try:
        r = requests.get(yts_api, params={"query_term": imdb_id})
    except requests.exceptions.ConnectionError:
        logger.info("yts api no responde.")
        return None
    if r.status_code == 200:
        torrent = r.json() # Dar url en lugar de hash.
        try:
            movie = torrent["data"]["movies"][0]['torrents'][0]
            url = movie['url']
            seeds = movie['seeds']
            size = movie['size']
            quality = movie['quality']

            return url, seeds, size, quality

        except (IndexError, KeyError) as e:
            logger.exception("There was a problem with yts api response")
