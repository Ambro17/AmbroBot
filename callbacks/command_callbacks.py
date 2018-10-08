import os

import requests

from command.movies.movie_utils import get_yt_trailer, get_torrent_info
from utils.command_utils import pretty_print_dolar


def dolarhoy_callback(banco_data, banco):
    """Shows only the info of desired banco from banco_data"""
    # Maybe we need some asociation between banco callback_data and the name of the key on the dict.
    # -> For now, callback data will match banco_data key, but this may be error prone (can we avoid that, tho?)
    # Filtrar en el dict la entrada que quiero o crear otra
    requested_banco = {k: v for k, v in banco_data.items() if k == banco}
    if requested_banco:
        return pretty_print_dolar(requested_banco)
    elif banco == 'Todos':
        return pretty_print_dolar(banco_data)

def peliculas_callback(movie, link_choice):
    """Gives link_choice of movie id.

    link_choice in ('IMDB', 'Magnet', 'Youtube', 'all')
    """
    params = {'api_key': os.environ['TMDB_KEY'], 'append_to_response': 'videos'}
    r = requests.get(f"https://api.themoviedb.org/3/movie/{movie['movie']}", params=params)
    data = r.json()
    imdb_id = data['imdb_id']
    if link_choice == 'IMDB':
        answer = f"[IMDB](http://www.imdb.com/title/{imdb_id})"
    elif link_choice == 'Youtube':
        answer = f"[Trailer]({get_yt_trailer(data['videos'])})"
    elif link_choice == 'Torrent':
        torrent = get_torrent_info(imdb_id)
        if torrent:
            url, seeds, size, quality = torrent
            answer = (
                f"🏴‍☠️ [.Torrent File]({url})\n\n"
                f"🌱 Seeds: {seeds}\n\n"
                f"🗳 Size: {size}\n\n"
                f"🖥 Quality: {quality}"
            )
        else:
            answer = "🚧 No torrent available for this movie."

    return answer

