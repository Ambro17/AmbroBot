import requests
from telegram.ext import run_async
import logging

from commands.pelicula.keyboard import pelis_keyboard
from commands.pelicula.utils import (
    request_movie,
    get_basic_info,
    prettify_basic_movie_info,
)
from updater import elbot
from utils.decorators import send_typing_action, log_time

logger = logging.getLogger(__name__)


@elbot.command(command=['pelicula', 'película'], pass_args=True, pass_chat_data=True)
@log_time
@send_typing_action
@run_async
def buscar_peli(bot, update, chat_data, args):
    pelicula = args
    if not pelicula:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Necesito que me pases una pelicula. `/pelicula <nombre>`',  # Todo: Add deeplink with example
            parse_mode='markdown',
        )
        return

    try:
        pelicula_query = ' '.join(pelicula)
        movie = request_movie(pelicula_query)
        if not movie:
            bot.send_message(
                chat_id=update.message.chat_id,
                text='No encontré info sobre %s' % pelicula_query,
            )
            return

        movie_info = get_basic_info(movie)
        # Give context to button handlers
        chat_data['context'] = {
            'data': {
                'movie': movie,
                'movie_basic': movie_info
            },
        }

        movie_details, poster = prettify_basic_movie_info(movie_info)
        if poster:
            bot.send_photo(chat_id=update.message.chat_id, photo=poster)

        update.message.reply_text(
            text=movie_details,
            reply_markup=pelis_keyboard(),
            parse_mode='markdown',
            disable_web_page_preview=True,
            quote=False,
        )
    except requests.exceptions.ConnectionError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Estoy descansando ahora, probá después de la siesta',
            parse_mode='markdown',
        )
    except Exception:
        logger.error('something bad happened')
        update.message.reply_text('Something bad happened, sorry')
