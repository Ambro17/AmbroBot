import requests
from telegram.ext import run_async

from commands.pelicula.utils import get_movie, prettify_movie
from utils.decorators import send_typing_action, log_time
from keyboards.keyboards import pelis_keyboard


@send_typing_action
@run_async
@log_time
def buscar_peli(bot, update, chat_data, **kwargs):
    pelicula = kwargs.get('args')
    if not pelicula:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Necesito que me pases una pelicula. `/pelicula <nombre>`',
            parse_mode='markdown'
        )
        return

    try:
        pelicula_query = ' '.join(pelicula)
        movie = get_movie(pelicula_query)
        if not movie:
            bot.send_message(
                chat_id=update.message.chat_id,
                text='No encontré info sobre %s' % pelicula_query,
            )
            return

        # Give context to button handlers
        chat_data['context'] = {
            'data': dict(movie_id=movie['id'], title=movie['title']),
            'command': 'pelicula',
            'edit_original_text': False,
        }

        movie_details, poster = prettify_movie(movie)
        keyboard = pelis_keyboard()
        bot.send_photo(chat_id=update.message.chat_id, photo=poster)
        bot.send_message(
            chat_id=update.message.chat_id,
            text=movie_details,
            reply_markup=keyboard,
            parse_mode='markdown',
            disable_web_page_preview=True,
        )
    except requests.exceptions.ConnectionError:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Estoy descansando ahora, probá después de la siesta',
            parse_mode='markdown',
        )
