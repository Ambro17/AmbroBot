from telegram.ext import run_async, CommandHandler

from commands.dolar.keyboards import banco_keyboard
from commands.dolar.utils import get_cotizaciones, pretty_print_dolar
from utils.decorators import send_typing_action, log_time
from utils.utils import soupify_url


@log_time
@send_typing_action
@run_async
def dolar_hoy(bot, update, chat_data):
    soup = soupify_url("http://www.dolarhoy.com/usd")
    data = soup.find_all('table')

    cotiz = get_cotizaciones(data)
    pretty_result = pretty_print_dolar(cotiz)

    chat_data['context'] = {
        'data': cotiz,
        'command': 'dolarhoy',
        'edit_original_text': True,
    }
    keyboard = banco_keyboard(cotiz)
    bot.send_message(
        update.message.chat_id,
        text=pretty_result,
        reply_markup=keyboard,
        parse_mode='markdown',
    )


dolar_handler = CommandHandler('dolar', dolar_hoy, pass_chat_data=True)
