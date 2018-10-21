from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from command.serie.constants import (
    LATEST_EPISODES,
    LOAD_EPISODES,
    GO_BACK_TO_MAIN,
    SEASON_T,
    EPISODE_T,
)


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
            Button('🎬️ Youtube', callback_data="Youtube"),
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
    return InlineKeyboardMarkup([[
        Button('Go back', callback_data=GO_BACK_TO_MAIN)
    ]])


def serie_season_keyboard(seasons):
    COLUMNS = 2
    buttons = [
        Button(f'Season {season}', callback_data=SEASON_T.format(season))
        for season, episodes in sorted(seasons.items())
    ]
    columned_keyboard= [
        buttons[i:i+COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]

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

    return InlineKeyboardMarkup(columned_keyboard)