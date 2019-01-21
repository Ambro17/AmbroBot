from telegram.ext import run_async, CommandHandler

from commands.hoypido.keyboard import hoypido_keyboard
from commands.hoypido.utils import get_comidas, prettify_food_offers
from utils.decorators import send_typing_action, log_time


@log_time
@send_typing_action
@run_async
def hoypido(bot, update, chat_data):
    comidas = get_comidas()
    pretty_comidas = prettify_food_offers(comidas)

    chat_data['context'] = {
        'data': comidas,
        'command': 'hoypido',
        'edit_original_text': True,
    }
    keyboard = hoypido_keyboard(comidas)
    bot.send_message(
        update.message.chat_id,
        text=pretty_comidas,
        reply_markup=keyboard,
        parse_mode='markdown',
    )


hoypido_handler = CommandHandler('hoypido', hoypido, pass_chat_data=True)
