import logging

from commands.dolar.callback import dolarhoy_callback
from commands.hoypido.callback import hoypido_callback
from commands.hoypido.keyboard import hoypido_keyboard
from commands.pelicula.callback import peliculas_callback
from keyboards.keyboards import banco_keyboard, pelis_keyboard

logger = logging.getLogger(__name__)

command_callback = {
    'dolarhoy': dolarhoy_callback,
    'pelicula': peliculas_callback,
    'hoypido': hoypido_callback,
}


def handle_callbacks(bot, update, chat_data):
    # Get the handler based on the commands
    context = chat_data.get('context')
    if not context:
        user = update.effective_user.first_name
        message = (f"Perdón {user}, no pude traer la info que me pediste.\n"
                   f"Probá invocando de nuevo el comando a ver si me sale 😊")
        logger.info(f"Conflicting update: '{update.to_dict()}'. Chat data: {chat_data}")
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode='markdown'
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    # Get user selection
    answer = update.callback_query.data

    callback_handler = command_callback[context['command']]

    # Get the relevant info based on user choice
    handled_response = callback_handler(context['data'], answer)
    # Notify that api we have succesfully handled the query
    update.callback_query.answer(text='')

    # Rebuild the same keyboard
    if context['command'] == 'dolarhoy':
        keyboard = banco_keyboard()
    elif context['command'] == 'pelicula':
        keyboard = pelis_keyboard()
    elif context['command'] == 'hoypido':
        comidas = context['data']
        keyboard = hoypido_keyboard(comidas)

    if context.get('edit_original_text'):
        update.callback_query.edit_message_text(
            text=handled_response, reply_markup=keyboard, parse_mode='markdown'
        )
    else:
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=handled_response,
            parse_mode='markdown'
        )
