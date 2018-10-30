import os

import requests

from commands.pelicula.utils import get_yts_torrent_info, get_yt_trailer
from utils.constants import IMDB_LINK


def peliculas_callback(movie, link_choice):
    """Gives link_choice of movie id.

    link_choice in ('IMDB', 'Magnet', 'Youtube', 'all')
    """
    params = {'api_key': os.environ['TMDB_KEY'], 'append_to_response': 'videos'}
    r = requests.get(f"https://api.themoviedb.org/3/movie/{movie['movie_id']}", params=params)
    data = r.json()
    imdb_id = data['imdb_id']
    if link_choice == 'IMDB':
        answer = f"[IMDB]({IMDB_LINK.format(imdb_id)}"
    elif link_choice == 'Youtube':
        answer = f"[Trailer]({get_yt_trailer(data['videos'])})"
    elif link_choice == 'Torrent':
        torrent = get_yts_torrent_info(imdb_id)
        if torrent:
            url, seeds, size, quality = torrent
            answer = (
                f"🏴‍☠️ [{movie['title']}]({url})\n\n"
                f"🌱 Seeds: {seeds}\n\n"
                f"🗳 Size: {size}\n\n"
                f"🖥 Quality: {quality}"
            )
        else:
            answer = "🚧 No torrent available for this movie."

    return answer
