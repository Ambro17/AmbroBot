from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.hoypido.utils import day_names
from commands.serie.constants import (
    LATEST_EPISODES,
    LOAD_EPISODES,
    GO_BACK_TO_MAIN,
    SEASON_T,
    EPISODE_T,
)
from commands.yts.constants import NEXT_YTS, YTS_TORRENT, IMDB_LINK, YT_LINK, YTS_FULL_DESC

@lru_cache(1)
def banco_keyboard():
    buttons = [
        [
            Button('Galicia', callback_data="Galicia"),
            Button('Nación', callback_data="Nación"),
            Button('Santander', callback_data="Santander"),
            Button('Francés', callback_data="Frances"),
            Button('Todos', callback_data="Todos"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


@lru_cache(1)
def pelis_keyboard():
    buttons = [
        [
            Button('🎟️ IMDB', callback_data="IMDB"),
            Button('🎬️ Trailer', callback_data="Youtube"),
            Button('🍿 Torrent', callback_data="Torrent"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def yts_navigator_keyboard(imdb_id=None, yt_trailer=None, show_next=True):
    buttons = [
        [
            Button('📖 Read more', callback_data=YTS_FULL_DESC),
        ],
        [
            Button('🍿 Torrent', callback_data=YTS_TORRENT),
            Button('🎟️ IMDB', url=IMDB_LINK.format(imdb_id)),
            Button('🎬️ Trailer', url=YT_LINK.format(yt_trailer))  # Todo: only add if yt_trailer is not None
        ]
    ] # Implement Back too
    if show_next:
        buttons[0].append(
            Button('Next »', callback_data=NEXT_YTS)
        )

    return InlineKeyboardMarkup(buttons)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu