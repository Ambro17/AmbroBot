from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.hoypido.utils import day_names


def hoypido_keyboard(comidas):
    weekday_buttons = [
        [
            Button(day_names[day_int], callback_data=day_int)
            for day_int in comidas.keys()
        ],
        [
            Button('🥕 Ir a Hoypido', url='https://www.hoypido.com/menu/onapsis.saludable')
        ]
    ]
    return InlineKeyboardMarkup(weekday_buttons)
