import requests
from telegram.ext import run_async

from utils.decorators import send_typing_action, log_time
from utils.utils import soupify_url


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
    try:
        logo, *info = info_de_partido(partido)
    except ValueError:
        update.message.reply_text('No pude leer el próximo partido.\n'
                                  'Podes chequearlo [acá](https://mundoazulgrana.com.ar/sanlorenzo/)',
                                  parse_mode='markdown')
        return
    bot.send_photo(chat_id=update.message.chat_id, photo=logo)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(info))


# Helper func for partido
def info_de_partido(partido):
    """
    <div class="cont">
        <img alt="Hurac�n" height="80" src="https://mundoazulgrana.com.ar/totaldata/img/escudos/01/54032.png" width="80"/>
    <div class="temp">20
        <span>ENE</span>
    </div>
    <p>18:00/FOX Sports Premium</p>
    <p>Pedro Bidegain/
        <a href="/sanlorenzo/futbol/arbitros/24/herrera.html">Herrera</a>
    </p>
    <p></p>
        <a href="/sanlorenzo/futbol/partido/3509/huracan.html">
            <button type="button">ver más</button>
        </a>
    </div>


    Args:
        partido: raw html of the site

    Returns:
        tuple: partido attributes
    """
    try:
        logo = partido.img.attrs['src']
        fecha = partido.find('div', {'class': 'temp'}).text
        hora_tv = partido.find('p').text
        estadio_arbitro = partido.p.find_next_sibling('p').text
    except Exception:
        raise ValueError('Website html has changed. Review parsing')

    return logo, fecha, hora_tv, estadio_arbitro
