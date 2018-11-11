from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.pelicula.constants import IMDB, YOUTUBE, TORRENT, SINOPSIS, SUBTITLES


@lru_cache(1)
def pelis_keyboard(include_desc=False):
    buttons = [
        [
            Button('🎟️ IMDB', callback_data=IMDB),
            Button('🎬️ Trailer', callback_data=YOUTUBE)
        ],
        [
            Button('🍿 Descargar', callback_data=TORRENT),
            Button('💬 Subs', callback_data=SUBTITLES),
        ]
    ]
    if include_desc:
        sinospsis_row = [Button('📖️ Sinopsis', callback_data=SINOPSIS)]
        buttons.insert(0, sinospsis_row)

    return InlineKeyboardMarkup(buttons)
