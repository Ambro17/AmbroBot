import re
from os.path import join as os_join, dirname, abspath

PELICULA = r'PELICULA_'

IMDB = PELICULA + 'IMDB'
YOUTUBE = PELICULA + 'YOUTUBE'
TORRENT = PELICULA + 'TORRENT'
SUBTITLES = PELICULA + 'SUBTITLES'
SINOPSIS = PELICULA + 'SINOPSIS'

PELICULA_REGEX = re.compile(PELICULA)

NO_TRAILER_MESSAGE = '💤 No hay trailer para esta pelicula'

SUBS_DIR = os_join(dirname(abspath(__file__)), 'subs')

LOADING_GIF = 'CgADBAADrqAAAqEeZAfb4Ot0k2Z7bAI'
cool = 'CgADBAAD46AAAuIaZAeIFKhwDWqvUQI'
acumulapunto = 'CgADBAAD46AAAuIaZAdTT7zJlgxNDQI'
green_loading = 'CgADBAAD-aAAAnUaZAfjftup41BQdAI'

LOADING_GIFS = [LOADING_GIF, cool, acumulapunto, green_loading]
