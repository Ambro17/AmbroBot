import numpy as np

from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

READ_MATRIX, SHOW_MATRIX, B_MATRIX, SOLVE_METHOD = range(4)

EXAMPLE_NOT_DDOM = "1 2 3\n4 5 6\n7 8 9"
EXAMPLE_DDOM_ROW = "5 3 1\n2 6 0\n1 2 4"
EXAMPLE_DDOM_COL = "5 3 3\n2 6 0\n1 2 4"

JACOBI = 'Jacobi'
GAUSS_SEIDEL = 'Gauss Seidel'

DETALLE = 'Detalle'
OTHER_METHOD = 'Otro'
SALIR = 'Salir'


def _parse_matrix(text):
    # assert nxn and diagonal.
    # assert nxn
    text = EXAMPLE_DDOM_ROW
    rows = text.split('\n')
    matrix = [list(map(int, r.split(' '))) for r in rows]
    return matrix


def show_matrix_markup(matrix):
    COLUMNS = len(matrix[0])
    buttons = [
        Button(f'{num}', callback_data='a')
        for row in matrix
        for num in row
    ]
    columned_keyboard = [
        buttons[i:i + COLUMNS] for i in range(0, len(buttons), COLUMNS)
    ]
    return InlineKeyboardMarkup(columned_keyboard)


def number_callback(bot, update, *args, **kwargs):
    """Ignore presses on matrix numbers"""
    update.callback_query.answer(text='')


def _is_diagonal_dominant(matrix):
    """Calculates if a matrix is diagonally dominant (by row or column)"""
    COLUMN, ROW = 0, 1
    abs_matrix = np.abs(matrix)

    return np.all(
        2 * np.diag(abs_matrix) >= np.sum(abs_matrix, axis=ROW)
    ) or np.all(
        2 * np.diag(abs_matrix) >= np.sum(abs_matrix, axis=COLUMN)
    )


def _is_square(matrix):
    return len(matrix) == len(matrix[0])


def equations_matrix_markup(a_matrix, b_matrix):
    COLUMNS = len(a_matrix[0])
    A_buttons = [
        Button(f'{num}', callback_data='a')
        for row in a_matrix
        for num in row
    ]
    columned_keyboard = [
        A_buttons[i:i + COLUMNS] for i in range(0, len(A_buttons), COLUMNS)
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


def aproximar_o_cancelar():
    buttons = [
        [
            Button('✅ Calcular', callback_data='Calcular'),
            Button('🚫 Cancelar', callback_data='/cancel')
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def aproximate(method, a_matrix, b_matrix, cota_de_error, decimals):
    return 1, 'el detalle'


opposite_method = {
    JACOBI: GAUSS_SEIDEL,
    GAUSS_SEIDEL: JACOBI,
}


def see_details_or_aproximate_by_other():
    buttons = [
        [
            Button('🔍 Detalle', callback_data=DETALLE),
            Button('🔁 Probar otro método', callback_data=OTHER_METHOD)
        ],
        [
            Button('🚪 Salir', callback_data=SALIR)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
