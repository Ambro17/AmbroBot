from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    RegexHandler,
    Filters,
)

from commands.aproximacion.state_handlers import (
    ingresar_matriz,
    read_matriz,
    read_coef_matrix_and_choose_method,
    solve_method,
    solve_method_by_text,
    read_method_parameters,
    calculate,
    details,
    cancel,
    default,
)
from commands.aproximacion.utils import number_callback


READ_MATRIX_A, READ_MATRIX_B, SOLVE_METHOD, METHOD_PARAMETERS, APROXIMAR, DETAILS = range(6)


msup_conversation = ConversationHandler(
    entry_points=[CommandHandler('aproximar', ingresar_matriz)],
    states={
        READ_MATRIX_A: [MessageHandler(Filters.text, read_matriz, pass_chat_data=True)],
        READ_MATRIX_B: [
            MessageHandler(
                Filters.text, read_coef_matrix_and_choose_method, pass_chat_data=True
            ),
            # If the user clicks on the matrix numbers stop the loading icon.
            CallbackQueryHandler(number_callback),
        ],
        SOLVE_METHOD: [
            CallbackQueryHandler(solve_method, pass_chat_data=True),
            RegexHandler(
                r'(jacobi|gauss|j|g)',
                solve_method_by_text,
                pass_chat_data=True,
                pass_groups=True,
            ),
        ],
        METHOD_PARAMETERS: [
            MessageHandler(Filters.text, read_method_parameters, pass_chat_data=True)
        ],
        APROXIMAR: [CallbackQueryHandler(calculate, pass_chat_data=True)],
        DETAILS: [CallbackQueryHandler(details, pass_chat_data=True)],
    },
    fallbacks=[CommandHandler('cancel', cancel), CallbackQueryHandler(default)],
)
