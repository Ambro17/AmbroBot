import requests
from telegram.ext import run_async

from utils.decorators import send_typing_action, log_time
from utils.command_utils import soupify_url


@log_time
@send_typing_action
@run_async
def partido(bot, update):
    try:
        soup = soupify_url('https://mundoazulgrana.com.ar/sanlorenzo/')
    except requests.exceptions.ReadTimeout:
        update.message.reply_text('En estos momentos no puedo darte esta info.')
        return
    partido = soup.find('div', {'class': 'widget-partido'}).find(
        'div', {'class': 'cont'}
    )
    logo, *info = info_de_partido(partido)
    bot.send_photo(chat_id=update.message.chat_id, photo=logo)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(info))


# Helper func for partido
def info_de_partido(partido):
    logo = partido.img.attrs['src']
    fecha = partido.find('div', {'class': 'temp'}).text
    hora, tv, estadio, arbitro = [p.text for p in partido.find_all('p') if p.text]
    return logo, fecha, hora, tv, estadio, arbitro
