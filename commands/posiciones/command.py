from telegram.ext import run_async

from commands.posiciones.utils import parse_posiciones, prettify_table_posiciones
from utils.decorators import send_typing_action, log_time
from utils.command_utils import soupify_url


@log_time
@send_typing_action
@run_async
def posiciones(bot, update, **kwargs):
    soup = soupify_url('http://www.promiedos.com.ar/primera', encoding='ISO-8859-1')
    tabla = soup.find('table', {'id': 'posiciones'})
    info = parse_posiciones(tabla, posiciones=kwargs.get('args'))
    pretty = prettify_table_posiciones(info)
    bot.send_message(chat_id=update.message.chat_id, text=pretty, parse_mode='markdown')
