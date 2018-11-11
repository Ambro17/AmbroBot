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

LOADING_GIF = 'CgADBAADrqAAAqEeZAcen_ivYBXU8AI'
cool = 'CgADBAADBgAD0xUtUIax4e74LDOjAg'
acumulapunto = 'CgADBAAD46AAAuIaZAdTT7zJlgxNDQI'
green_loading = 'CgADBAAD-aAAAnUaZAc-Q7x3aeH_IgI'

LOADING_GIFS = [LOADING_GIF, cool, acumulapunto, green_loading]
