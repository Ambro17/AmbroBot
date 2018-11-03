from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.remindme.constants import MINUTE, HOUR


def time_options_keyboard():
    buttons = [
        [
            Button('5 Mins', callback_data=5 * MINUTE),
            Button('10 Mins', callback_data=10 * MINUTE),
            Button('20 Mins', callback_data=20 * MINUTE),
            Button('30 Mins', callback_data=30 * MINUTE),
        ],
        [
            Button('1 Hour', callback_data=HOUR),
            Button('2 Hours', callback_data=2 * HOUR),
            Button('4 Hours', callback_data=4 * HOUR),
            Button('8 Hours', callback_data=8 * HOUR)
        ],
        [
            Button('12 hours', callback_data=12 * HOUR),
            Button('24 hours', callback_data=24 * HOUR),
        ]
    ]
    # Add Button('Guess from input', callback_data=GUESS_FROM_INPUT)
    return InlineKeyboardMarkup(buttons)
