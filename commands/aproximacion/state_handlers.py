import logging

import numpy as np
from telegram.ext import ConversationHandler

from commands.aproximacion.utils import EXAMPLE_NOT_DDOM, _parse_matrix, _is_square, _is_diagonal_dominant, \
    show_matrix_markup, equations_matrix_markup, JACOBI, GAUSS_SEIDEL, aproximar_o_cancelar, aproximate, \
    see_details_or_aproximate_by_other, DETALLE, OTHER_METHOD, EXPORT_CSV, prettify_details, opposite_method, \
    dump_results_to_csv
from utils.command_utils import monospace
from utils.decorators import send_typing_action

READ_MATRIX_A, READ_MATRIX_B, SOLVE_METHOD, METHOD_PARAMETERS, APROXIMAR, DETAILS = range(6)


logger = logging.getLogger(__name__)


@send_typing_action
def ingresar_matriz(bot, update):
    update.message.reply_text(
        'Ingresar matriz A. El formato es:\n' +
        monospace(EXAMPLE_NOT_DDOM),
        parse_mode='markdown'
    )
    return READ_MATRIX_A


# First state
def read_matriz(bot, update, chat_data):
    matrix = _parse_matrix(update.message.text)
    is_square_matrix = _is_square(matrix)
    is_diag_dominant = _is_diagonal_dominant(matrix)
    if not is_diag_dominant:
        update.message.reply_text(
            text=f'🚫 La matriz ingresada no es diagonalmente dominante.\nIntentá de nuevo',
        )
        return READ_MATRIX_A
    if not is_square_matrix:
        update.message.reply_text(
            text=f'🚫 La matriz ingresada no es cuadrada.\nIntentá de nuevo',
        )
        return READ_MATRIX_A

    chat_data['matrix'] = matrix
    logger.info("A: %s", matrix)

    update.message.reply_text(
        text=f'✅ La matriz ingresada es diagonalmente dominante:',
        reply_markup=show_matrix_markup(matrix)
    )
    update.message.reply_text(
        text='Ahora Ingresa la matriz de coeficientes (B). Ejemplo `1 2 3`',
        parse_mode='markdown'
    )
    return READ_MATRIX_B


# Second state
def read_coef_matrix_and_choose_method(bot, update, chat_data):
    b_matrix = update.message.text.split(' ')

    required_coefs = len(chat_data['matrix'])
    if len(b_matrix) != required_coefs:
        update.message.reply_text(
            f'🚫 Los coeficientes deben ser {required_coefs} pero ingresaste {len(b_matrix)}\n'
            'Volvé a intentarlo separando con un espacio cada coeficiente 🙏'
        )
        return READ_MATRIX_B

    chat_data['matrix_b'] = b_matrix
    logger.info("B: %s", b_matrix)

    a_matrix = chat_data['matrix']
    update.message.reply_text(
        'Elegí el método de resolución o apreta /cancel si ves algo mal.\n'
        'El sistema de ecuaciones lineales es el siguiente:',
        reply_markup=equations_matrix_markup(a_matrix, b_matrix)
    )
    return SOLVE_METHOD


# Third State
def solve_method(bot, update, chat_data):
    method = update.callback_query.data
    if method not in (JACOBI, GAUSS_SEIDEL):
        # A number, or the equal sign was pressed. Ignore it
        update.callback_query.answer(text='')
        return SOLVE_METHOD

    chat_data['chosen_method'] = method
    logger.info(f'Método: {method}')

    update.callback_query.answer(text='')
    update.callback_query.message.reply_text(
        f'Elegiste el metodo `{method}`.\n'
        'Elegí el vector inicial, la cota de error y la cantidad de decimales.\n'
        'El formato es: `0 0 0; 0.001; 4`',
        parse_mode='markdown'
    )

    return METHOD_PARAMETERS


# Third state message handler (not callback)
def solve_method_by_text(bot, update, chat_data, groups):
    method = update.message.text
    if method in ('j', 'jacobi'):
        method = JACOBI
        chat_data['chosen_method'] = JACOBI
    elif method in ('g', 'gauss'):
        method = GAUSS_SEIDEL
        chat_data['chosen_method'] = method
    else:
        # Ignore update
        logger.info("Ignoring response %s" % method)
        return

    logger.info(f'Método: {method}')

    update.message.reply_text(
        f'Elegiste el metodo `{method}`.\n'
        'Elegí el vector inicial, la cota de error y la cantidad de decimales.\n'
        'El formato es: `0 0 0; 0.001; 4`',
        parse_mode='markdown'
    )

    return METHOD_PARAMETERS


# Fourth State
def read_method_parameters(bot, update, chat_data):
    params = update.message.text.split(';')
    if len(params) != 3:
        update.message.reply_text('No ingresaste bien la data. Asegurate de separar por ; (punto y coma)')
        return METHOD_PARAMETERS

    v_inicial, cota, cant_decimales = [p.strip() for p in params]
    chat_data['v_inicial'] = v_inicial
    chat_data['cant_decimales'] = int(cant_decimales)
    chat_data['cota'] = float(cota)
    logger.info(f"V_0: {v_inicial}, decimales: {cant_decimales}, cota de error: {cota}")

    update.message.reply_text(
        f"Método de resolución `{chat_data['chosen_method']}`\n"
        f"Vector inicial: `{v_inicial}`\n"
        f"Cantidad de decimales: `{cant_decimales}`\n"
        f"Cota de error: `{cota}`\n",
        parse_mode='markdown',
        reply_markup=aproximar_o_cancelar()
    )
    return APROXIMAR


# Fifth State
def calculate(bot, update, chat_data):
    if update.callback_query.data == '/cancel':
        return cancel(bot, update)

    a_matrix = chat_data['matrix']
    b_matrix = list(map(int, chat_data['matrix_b']))
    v_inicial = list(map(int, chat_data['v_inicial'].split(' ')))  # '0 0 0' to [0, 0, 0]
    cota_de_error = chat_data['cota']
    decimals = chat_data['cant_decimales']
    method = chat_data['chosen_method']

    result, details = aproximate(method, a_matrix, b_matrix, cota_de_error, v_inicial, decimals)
    chat_data['result'] = result
    chat_data['result_details'] = details

    update.callback_query.answer(text='')
    np.set_printoptions(precision=decimals)
    update.callback_query.message.reply_text(
        f"El resultado de la aproximación via `{chat_data['chosen_method']}` es:\n`{result}`",
        parse_mode='markdown',
        reply_markup=see_details_or_aproximate_by_other()
    )
    return DETAILS


# 6th State
def details(bot, update, chat_data):
    answer = update.callback_query.data
    update.callback_query.answer(text='')
    if answer == DETALLE:
        result_steps = chat_data['result_details']
        details = prettify_details(result_steps, chat_data['cant_decimales'])
        update.callback_query.message.reply_text(
            monospace(details),
            parse_mode='markdown'
        )
    elif answer == OTHER_METHOD:
        chat_data['chosen_method'] = opposite_method[chat_data['chosen_method']]
        return calculate(bot, update, chat_data)

    elif answer == EXPORT_CSV:
        csv_results = dump_results_to_csv(
            chat_data['result'], chat_data['result_details'], chat_data['cant_decimales'], chat_data['cota'])
        bot.send_document(
            chat_id=update.callback_query.message.chat_id,
            document=open(csv_results, 'rb')
        )
    else:
        update.callback_query.message.edit_text('🏳 Mi trabajo aquí ha terminado', reply_markup=None)
        return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('👮🏾‍♀️ Operación cancelada')
    return ConversationHandler.END


def default(bot, update):
    update.callback_query.answer(text='')
    update.callback_query.message.edit_text('🤕 Algo me confundió. Podemos empezar de nuevo con /aproximar',
                                            reply_markup=None)
    return ConversationHandler.END