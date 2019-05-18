from telegram.ext import run_async, CommandHandler

from commands.posiciones.utils import parse_posiciones, prettify_table_posiciones
from updater import elbot
from utils.decorators import send_typing_action, log_time
from utils.utils import soupify_url


@log_time
@send_typing_action
@run_async
@elbot.route(command='posiciones', pass_args=True)
def posiciones(bot, update, args):
    soup = soupify_url('http://www.promiedos.com.ar/primera', encoding='ISO-8859-1')
    tabla = soup.find('table', {'id': 'posiciones'})
    info = parse_posiciones(tabla, posiciones=args[0] if args else None)
    pretty = prettify_table_posiciones(info)
    bot.send_message(chat_id=update.message.chat_id, text=pretty, parse_mode='markdown')
