import csv
import logging

import numpy as np

from commands.aproximacion.constants import JACOBI, GAUSS_SEIDEL
from commands.aproximacion.gauss_seidel import solve_by_gauss_seidel
from commands.aproximacion.jacobi import solve_by_jacobi


methods = {
    JACOBI: solve_by_jacobi,
    GAUSS_SEIDEL: solve_by_gauss_seidel
}


logger = logging.getLogger(__name__)


def _parse_matrix(text):
    rows = text.split('\n')
    matrix = [list(map(int, r.split(' '))) for r in rows]
    return matrix


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