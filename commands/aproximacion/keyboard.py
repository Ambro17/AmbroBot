from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.aproximacion.constants import (
    JACOBI,
    GAUSS_SEIDEL,
    DETALLE,
    EXPORT_CSV,
    OTHER_METHOD,
    SALIR,
)


def equations_matrix_markup(a_matrix, b_matrix):
    COLUMNS = len(a_matrix[0])
    A_buttons = [
        Button(f'{num}', callback_data='a')
        for row in a_matrix
        for num in row
    ]
    columned_keyboard = [
        A_buttons[i: i + COLUMNS] for i in range(0, len(A_buttons), COLUMNS)
    ]
    # add b coef with a space
    for row, b_value in zip(columned_keyboard, b_matrix):
        row.append(Button('=', callback_data='empty'))
        row.append(Button(f'{b_value}', callback_data='b_value'))

    # Append resolution methods
    jacobi = Button('🤓 Jacobi', callback_data=JACOBI)
    gauss_seidel = Button('🔢 Gauss Seidel', callback_data=GAUSS_SEIDEL)
    method_selector = [jacobi, gauss_seidel]

    columned_keyboard.append(method_selector)

    return InlineKeyboardMarkup(columned_keyboard)


def see_details_or_aproximate_by_other():
    buttons = [
        [
            Button('🔍 Detalle', callback_data=DETALLE),
            Button('🖇 Exportar', callback_data=EXPORT_CSV),
        ],
        [Button('🔁 Cambiar Método ', callback_data=OTHER_METHOD)],
        [Button('🚪 Salir', callback_data=SALIR)],
    ]
    return InlineKeyboardMarkup(buttons)


def show_matrix_markup(matrix):
    COLUMNS = len(matrix[0])
    buttons = [
        Button(f'{num}', callback_data='a')
        for row in matrix
        for num in row
    ]
    columned_keyboard = [
        buttons[i: i + COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    return InlineKeyboardMarkup(columned_keyboard)


def aproximar_o_cancelar():
    buttons = [
        [
            Button('✅ Calcular', callback_data='Calcular'),
            Button('🚫 Cancelar', callback_data='/cancel'),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
