from callbacks.command_callbacks import dolarhoy_callback, peliculas_callback, hoypido_callback
from keyboards.keyboards import banco_keyboard, pelis_keyboard, hoypido_keyboard

command_callback = {
    'dolarhoy': dolarhoy_callback,
    'pelicula': peliculas_callback,
    'hoypido': hoypido_callback,
}


def handle_callbacks(bot, update, chat_data):
    # Get the handler based on the command
    context = chat_data.get('context')
    if not context:
        message = f"Ups.. 😳 no pude encontrar lo que me pediste.\n" \
                  f"Podés probar invocando de nuevo el comando a ver si me sale 😊"
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
    else:
        keyboard = hoypido_keyboard()

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
