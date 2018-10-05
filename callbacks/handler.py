from callbacks.command_callbacks import dolarhoy_callback
from keyboards.bancos_keyboard import banco_keyboard

command_callback = {
    'dolarhoy': dolarhoy_callback
}


def handle_callbacks(bot, update, chat_data):
    # Rebuild the same keyboard
    keyboard = banco_keyboard()

    # Get user selection
    answer = update.callback_query.data
    # Get the hanlder based on the command
    chat_data = chat_data['context']

    callback_handler = command_callback[chat_data['command']]
    # Get the relevant info based on user choice
    handled_response = callback_handler(chat_data['data'], answer)

    original_text = update.callback_query.message.text

    update.callback_query.edit_message_text(
        text=handled_response,
        reply_markup=keyboard,
        parse_mode='markdown'
    )