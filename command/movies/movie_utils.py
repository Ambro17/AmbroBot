import requests
import logging
from  urllib.parse import quote_plus as encode_for_url

TMDB_KEY = '7f76943e1557e33276e0f595c2128f68'
logger = logging.getLogger(__name__)
def search_movie(pelicula):
    params = {'api_key': TMDB_KEY, 'query': pelicula}
    r = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
    if r.status_code == 200:
        movies = r.json()['results']
        if movies:
            movie_info = get_movie_info(movies[0])
            message = prettify_movie_info(*movie_info)
        else:
            message = 'No conozco ninguna peli bajo ese nombre..'
    else:
        message = 'Imdb se fue de vacaciones'

    return message

def get_movie_info(movie):
    title = movie['title']
    rating = movie['vote_average']
    overview = movie['overview']
    year = movie['release_date'].split('-')[0] # "2016-07-27" -> 2016
    # Get yt_trailer, imdb_link and magnet.
    params = {'api_key': TMDB_KEY, 'append_to_response': 'videos'}
    r = requests.get(f"https://api.themoviedb.org/3/movie/{movie['id']}",
                     params=params)
    data = r.json()
    imdb_id = data['imdb_id']
    imdb_link = f"http://www.imdb.com/title/{imdb_id}"
    yt_trailer = get_yt_trailer(data)
    magnet = search_magnet_link(title, imdb_id)
    return title, rating, overview, year, imdb_link, yt_trailer, magnet

def get_yt_trailer(data):
    key = data['videos']['results'][0]['key']
    return f'https://www.youtube.com/watch?v={key}'

def prettify_movie_info(title, rating, overview, year, imdb, yt, magnet):
    stars = int(rating // 2)
    imdb_line = f'[🎭 IMDB]({imdb})'
    yt_line = f'[▶ Trailer]({yt})'
#    magnet = f'🏴‍☠[MAGNET]({magnet})'  # Telegram does not detect magnet links
    return f"{title} ({year})\n{'⭐'*stars}\n\n{overview}\n\n{imdb_line} | {yt_line}"



def get_trackers():
    "URL encode trackers with &tr=prefix"
    trackers = ['udp://tracker.opentrackr.org:1337/announce',
                'udp://torrent.gresille.org:80/announce',
                'udp://tracker.openbittorrent.com:80',
                'udp://tracker.coppersurfer.tk:6969',
                'udp://tracker.leechers-paradise.org:6969',
                'udp://p4p.arenabg.ch:1337',
                'udp://tracker.internetwarriors.net:1337']

    return ''.join(
        f'&tr={tracker}' for tracker in trackers
    )

def search_magnet_link(title, imdb_id):
    MAGNET = "magnet:?xt=urn:btih:{torrent_hash}&dn={movie_name}{trackers}"
    jash = request_hash_from_yts(imdb_id)
    if jash:
        return MAGNET.format(
            torrent_hash=jash,
            movie_name=encode_for_url(title),
            trackers=get_trackers()
        )
    return None

def request_hash_from_yts(imdb_id):
    BEST_QUALITY = -1
    yts_api = 'https://yts.am/api/v2/list_movies.json'
    r = requests.get(yts_api, params={
        "query_term": imdb_id
    })
    if r.status_code == 200:
        torrent = r.json()
        try:
            return torrent["data"]["movies"][0]["torrents"][BEST_QUALITY]["hash"]
        except Exception as e:
            logger.exception("Something bad happened")

