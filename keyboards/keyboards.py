from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.serie.constants import (
    LATEST_EPISODES,
    LOAD_EPISODES,
    GO_BACK_TO_MAIN,
    SEASON_T,
    EPISODE_T,
)
from commands.yts.constants import NEXT_YTS, YTS_TORRENT, IMDB_LINK, YT_LINK

GO_BACK_BUTTON = [Button('« Back to Main', callback_data=GO_BACK_TO_MAIN)]

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
            Button('💀 Torrent', callback_data="Torrent"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


@lru_cache(1)
def hoypido_keyboard():
    weekday_buttons = [
        [
            Button(day, callback_data=i)
            for i, day in enumerate(('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'))
        ]
    ]
    return InlineKeyboardMarkup(weekday_buttons)


@lru_cache(1)
def serie_keyboard():
    buttons = [
        [
            Button('Latest episodes', callback_data=LATEST_EPISODES),
            Button('Load all episodes', callback_data=LOAD_EPISODES)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def serie_go_back_keyboard():
    return InlineKeyboardMarkup([GO_BACK_BUTTON])


def serie_season_keyboard(seasons):
    COLUMNS = 2
    buttons = [
        Button(f'Season {season}', callback_data=SEASON_T.format(season))
        for season, episodes in sorted(seasons.items())
    ]
    columned_keyboard= [
        buttons[i:i+COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    columned_keyboard.append(GO_BACK_BUTTON)

    return InlineKeyboardMarkup(columned_keyboard)


def serie_episodes_keyboards(episodes_dict):
    COLUMNS = 5
    buttons = [
        Button(f'Ep {ep_number}', callback_data=EPISODE_T.format(ep_number))
        for ep_number, episode in sorted(episodes_dict.items())
    ]
    columned_keyboard= [
        buttons[i:i+COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    columned_keyboard.append(GO_BACK_BUTTON)

    return InlineKeyboardMarkup(columned_keyboard)


def yts_navigator_keyboard(imdb_id=None, yt_trailer=None, show_next=True):
    buttons = [
        [
            Button('☠️ Torrent', callback_data=YTS_TORRENT),
            Button('🎟️ IMDB', url=IMDB_LINK.format(imdb_id)),
            Button('🎬️ Trailer', url=YT_LINK.format(yt_trailer))
        ]
    ] # Implement Back too
    if show_next:
        buttons.insert(0, [Button('Next', callback_data=NEXT_YTS)])
    return InlineKeyboardMarkup(buttons)

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu