#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton as Button
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

import logging

# Enable logging
from cnv_utils import _parse_matrix, number_callback, equations_matrix_markup, _is_square, _is_diagonal_dominant, \
    show_matrix_markup, aproximar_o_cancelar, see_details_or_aproximate_by_other, DETALLE, OTHER_METHOD, aproximate, \
    opposite_method
from utils.command_utils import monospace
from utils.decorators import send_typing_action

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

READ_MATRIX_A, READ_MATRIX_B, SOLVE_METHOD, METHOD_PARAMETERS, APROXIMAR, DETAILS = range(6)

EXAMPLE_NOT_DDOM = "1 2 3\n4 5 6\n7 8 9"
EXAMPLE_DDOM_ROW = "5 3 1\n2 6 0\n1 2 4"
EXAMPLE_DDOM_COL = "5 3 3\n2 6 0\n1 2 4"

JACOBI = 'Jacobi'
GAUSS_SEIDEL = 'Gauss Seidel'


# Initial state
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
        'El sistema de ecuaciones lineales es el siguiente:\n'
        'Elegí el método de resolución o apreta /cancel si ves algo mal.',
        reply_markup=equations_matrix_markup(a_matrix, b_matrix)
    )
    return SOLVE_METHOD


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
        'Elegí el vector inicial, la cantidad de decimales y la cota de error.\n'
        'El formato es: `0 0 0; 3; 0.001`',
        parse_mode='markdown'
    )

    return METHOD_PARAMETERS


def read_method_parameters(bot, update, chat_data):
    params = update.message.text.split(';')
    if len(params) != 3:
        update.message.reply_text('No ingresaste bien la data. Asegurate de separar por ; (punto y coma)')
        return METHOD_PARAMETERS

    v_inicial, cant_decimales, cota = [p.strip() for p in params]
    chat_data['v_inicial'] = v_inicial
    chat_data['cant_decimales'] = cant_decimales
    chat_data['cota'] = cota
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


def calculate(bot, update, chat_data):
    if update.callback_query.data == '/cancel':
        return cancel(bot, update)

    a_matrix = chat_data['matrix']
    b_matrix = chat_data['matrix_b']
    cota_de_error = chat_data['cota']
    decimals = chat_data['cant_decimales']
    method = chat_data['chosen_method']

    result, details = aproximate(method, a_matrix, b_matrix, cota_de_error, decimals)
    chat_data['result'] = result
    chat_data['result_details'] = details

    update.callback_query.answer(text='')
    update.callback_query.message.reply_text(
        f"El resultado de la aproximación via {chat_data['chosen_method']} es `{result}`",
        parse_mode='markdown',
        reply_markup=see_details_or_aproximate_by_other()
    )
    return DETAILS


def details(bot, update, chat_data):
    answer = update.callback_query.data
    update.callback_query.answer(text='')
    if answer == DETALLE:
        result_steps = chat_data['result_details']
        update.callback_query.message.reply_text(
            monospace(result_steps),
            parse_mode='markdown'
        )
    elif answer == OTHER_METHOD:
        chat_data['chosen_method'] = opposite_method[chat_data['chosen_method']]
        return calculate(bot, update, chat_data)
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


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ['PYTEL'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    msup_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('ap', ingresar_matriz)
        ],
        states={
            READ_MATRIX_A: [MessageHandler(Filters.text, read_matriz, pass_chat_data=True)],

            READ_MATRIX_B: [
                MessageHandler(Filters.text, read_coef_matrix_and_choose_method, pass_chat_data=True),
                # If the user clicks on the matrix numbers stop the loading icon.
                CallbackQueryHandler(number_callback)
            ],

            SOLVE_METHOD: [CallbackQueryHandler(solve_method, pass_chat_data=True)],

            METHOD_PARAMETERS: [MessageHandler(Filters.text, read_method_parameters, pass_chat_data=True)],

            APROXIMAR: [CallbackQueryHandler(calculate, pass_chat_data=True)],

            DETAILS: [CallbackQueryHandler(details, pass_chat_data=True)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(default)
        ]
    )

    dispatcher.add_handler(msup_conversation)

    updater.start_polling()


if __name__ == '__main__':
    main()
