from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.meeting.constants import DAY_T, CANCEL, MEETING_PERIOD


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


def repeat_interval_keyboard():
    buttons = [
        [
            Button('Semanalmente', callback_data=MEETING_PERIOD.format("Weekly")),
            Button('Bisemanalmente', callback_data=MEETING_PERIOD.format("Biweekly")),
            Button('Mensualmente', callback_data=MEETING_PERIOD.format("Monthly")),
        ],
        [
            Button('🚫 Cancel', callback_data=CANCEL)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
