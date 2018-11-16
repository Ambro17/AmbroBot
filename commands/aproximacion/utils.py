import csv
import logging

import numpy as np
from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from commands.aproximacion.gauss_seidel import solve_by_gauss_seidel
from commands.aproximacion.jacobi import solve_by_jacobi

JACOBI = 'Jacobi'
GAUSS_SEIDEL = 'Gauss Seidel'

methods = {
    JACOBI: solve_by_jacobi,
    GAUSS_SEIDEL: solve_by_gauss_seidel
}


logger = logging.getLogger(__name__)


EXAMPLE_NOT_DDOM = "1 2 3\n4 5 6\n7 8 9"
EXAMPLE_DDOM_ROW = "5 3 1\n2 6 0\n1 2 4"
EXAMPLE_DDOM_COL = "5 3 3\n2 6 0\n1 2 4"

DETALLE = 'Detalle'
OTHER_METHOD = 'Otro'
EXPORT_CSV = 'Exportar'
SALIR = 'Salir'


def _parse_matrix(text):
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


def aproximate(method, a_matrix, b_matrix, cota_de_error, v_inicial, decimals):
    apromixation_method = methods[method]
    logger.info('Invocando a metodo %s con args: A: %s, B: %s, cota: %s, v_inicial: %s' %
                (apromixation_method, a_matrix, b_matrix, cota_de_error, v_inicial))
    res, details = apromixation_method(a_matrix, b_matrix, cota_de_error, v_inicial)
    return res, details


opposite_method = {
    JACOBI: GAUSS_SEIDEL,
    GAUSS_SEIDEL: JACOBI,
}


def see_details_or_aproximate_by_other():
    buttons = [
        [
            Button('🔍 Detalle', callback_data=DETALLE),
            Button('🖇 Exportar', callback_data=EXPORT_CSV)
        ],
        [
            Button('🔁 Cambiar Método ', callback_data=OTHER_METHOD),
        ],
        [
            Button('🚪 Salir', callback_data=SALIR)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def prettify_details(result_steps, limit):
    # Prettify np.arrays into markdown pretty
    return '\n'.join(
        f"#{i:<2} | {_minify_array(results[0], limit)}"
        for i, results in enumerate(result_steps)
    )


def _minify_array(array, limit):
    return tuple([f'{elem:.{limit}f}' for elem in list(array)])


def dump_results_to_csv(final_result, result_steps, decimal_precision, error_minimo):
    FILE_PATH = 'aproximation_result.csv'
    solution_len = len(final_result)

    with open(FILE_PATH, mode='w') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        coordinates = [f'X_{i}' for i in range(solution_len)]
        csv_writer.writerow(['i'] + coordinates + ['Norma 1', 'Norma 2', 'Norma 3', 'Criterio de Paro'])

        for i, step in enumerate(result_steps):
            array_elems = [round(number, decimal_precision) for number in step[0]]
            normas = [round(norma, decimal_precision) if norma != '-' else '-'
                      for norma in step[1:]
                      ]
            row = [i] + array_elems + normas + [error_minimo]
            csv_writer.writerow(row)

    return FILE_PATH