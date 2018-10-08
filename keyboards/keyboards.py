from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button


@lru_cache(10)
def banco_keyboard():
    buttons = [
        [
            Button('Galicia', callback_data="Galicia"),
            Button('Nación', callback_data="Nacion"),
            Button('Santander', callback_data="Santander"),
            Button('Francés', callback_data="Frances"),
            Button('Todos', callback_data="Todos"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@lru_cache(10)
def pelis_keyboard():
    buttons = [
        [
            Button('🎟️ IMDB', callback_data="IMDB"),
            Button('▶️ Youtube', callback_data="Youtube"),
            Button('💀 Torrent', callback_data="Torrent"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)