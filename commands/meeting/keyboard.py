from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.meeting.constants import DAY_T


def days_selector_keyboard():
    # Show days and recurrence. Every week, every two weeks, once?
    buttons = [
         [
             Button(dia, callback_data=DAY_T.format(dia))
             for dia in ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes')
         ]
    ]
    # Add second keyboard with weekly, biweekly and monthly.
    return InlineKeyboardMarkup(buttons)