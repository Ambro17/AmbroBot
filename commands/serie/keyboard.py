from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.serie.constants import (
    GO_BACK_TO_MAIN,
    SEASON_T,
    EPISODE_T,
    LATEST_EPISODES,
    LOAD_EPISODES,
    LOAD_MORE_LATEST)


GO_BACK_BUTTON_ROW = [Button('« Back to Main', callback_data=GO_BACK_TO_MAIN)]

@lru_cache(1)
def serie_main_keyboard():
    buttons = [
        [
            Button('Latest episodes', callback_data=LATEST_EPISODES),
            Button('Load all episodes', callback_data=LOAD_EPISODES)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def serie_go_back_keyboard():
    return InlineKeyboardMarkup([GO_BACK_BUTTON_ROW])

def serie_load_more_latest_episodes_keyboard():
    buttons = [
        [
            Button('Load more..', callback_data=LOAD_MORE_LATEST)
        ],
        GO_BACK_BUTTON_ROW
    ]
    return InlineKeyboardMarkup(buttons)


def serie_season_keyboard(seasons):
    COLUMNS = 2
    buttons = [
        Button(f'Season {season}', callback_data=SEASON_T.format(season))
        for season, episodes in sorted(seasons.items())
    ]
    columned_keyboard= [
        buttons[i:i+COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    columned_keyboard.append(GO_BACK_BUTTON_ROW)

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
    columned_keyboard.append(GO_BACK_BUTTON_ROW)

    return InlineKeyboardMarkup(columned_keyboard)
