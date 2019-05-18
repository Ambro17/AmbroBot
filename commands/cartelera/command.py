from telegram.ext import run_async, CommandHandler

from updater import elbot
from utils.decorators import send_typing_action, log_time
from utils.utils import soupify_url


@log_time
@send_typing_action
@run_async
@elbot.route(command='cartelera')
def cinearg(bot, update):
    """Get top 5 Argentina movies"""
    CINE_URL = 'https://www.cinesargentinos.com.ar/cartelera'
    soup = soupify_url(CINE_URL)
    cartelera = soup.find('div', {'class': 'contenidoRankingContainer'})
    listado = [
        (rank, li.text, CINE_URL + li.a['href'])
        for rank, li in enumerate(cartelera.div.ol.find_all('li'), 1)
    ]
    top_5 = '\n'.join(f'[{rank}. {title}]({link})' for rank, title, link in listado[:5])
    bot.send_message(chat_id=update.message.chat_id, text=top_5, parse_mode='markdown')
