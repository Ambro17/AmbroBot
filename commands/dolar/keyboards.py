from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button


def banco_keyboard(cotizaciones):
    COLUMNS = 3
    buttons = [
        Button(f'{banco}', callback_data=banco)
        for banco in cotizaciones
    ]
    columned_keyboard = [
        buttons[i: i + COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    columned_keyboard.append([
        Button('💰 Todos', callback_data='Todos')
    ])
    return InlineKeyboardMarkup(columned_keyboard)
