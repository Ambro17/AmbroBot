import requests
import logging
from urllib.parse import quote_plus as encode_for_url

from command.movies.torrents import magnet_to_torrent

TMDB_KEY = '7f76943e1557e33276e0f595c2128f68'
logger = logging.getLogger(__name__)


def get_movie(pelicula_query):
    params = {'api_key': TMDB_KEY, 'query': pelicula_query, 'language': 'es-AR'}
    r = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    if r.status_code == 200:
        try:
            movies = r.json()['results'][0]
            return movies
        except (IndexError, KeyError):
            return None


def prettify_movie(movie_dict):
    movie_info = get_basic_info(movie_dict)
    message = prettify_basic_movie_info(*movie_info)

    return message


def get_basic_info(movie):
    title = movie['title']
    rating = movie['vote_average']
    overview = movie['overview']
    year = movie['release_date'].split('-')[0]  # "2016-07-27" -> 2016
    return title, rating, overview, year


def prettify_basic_movie_info(title, rating, overview, year):
    stars = int(rating // 2)
    return (
        f"{title} ({year})\n"
        f"{'⭐'*stars} ~ {rating}\n\n"
        f"{overview}\n\n"
    )


def get_yt_trailer(videos):
    key = videos['results'][-1]['key']
    return f'https://www.youtube.com/watch?v={key}'


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
