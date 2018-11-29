from functools import lru_cache

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.yts.constants import (
    NEXT_YTS,
    YTS_TORRENT,
    IMDB_LINK,
    YT_LINK,
    YTS_FULL_DESC,
)


def yts_navigator_keyboard(imdb_id=None, yt_trailer=None, show_next=True):
    buttons = [
        [Button('📖 Read more', callback_data=YTS_FULL_DESC)],
        [
            Button('🍿 Torrent', callback_data=YTS_TORRENT),
            Button('🎟️ IMDB', url=IMDB_LINK.format(imdb_id)),
            Button('🎬️ Trailer', url=YT_LINK.format(yt_trailer)),  # Todo: only add if yt_trailer is not None
        ],
    ]  # Implement Back too
    if show_next:
        buttons[0].append(Button('Next »', callback_data=NEXT_YTS))

    return InlineKeyboardMarkup(buttons)

