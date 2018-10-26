import logging
from telegram import InputMediaPhoto
from telegram.error import TimedOut

from commands.yts.constants import NEXT_YTS, YTS_TORRENT, YTS_FULL_DESC
from commands.yts.utils import get_torrents, prettify_torrent, get_minimal_movie, prettify_yts_movie, get_photo
from keyboards.keyboards import yts_navigator_keyboard

logger = logging.getLogger(__name__)


def handle_callback(bot, update, chat_data):
    # Get the handler based on the commands
    context = chat_data.get('context')
    if not context:
        message = (f"Mmm me falta info para resolver lo que pediste 🤔\n"
                   f"Probá invocando el comando de nuevo")
        logger.info(f"Conflicting update: '{update.to_dict()}'. Chat data: {chat_data}")
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode='markdown'
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    movies = context['data']
    current_movie = context['movie_number']
    next_movie = current_movie + 1

    # Get user selection
    answer = update.callback_query.data
    if answer == NEXT_YTS:
        # User wants to see info for next movie
        try:
            movie = movies[next_movie]
            logger.info(f"Requested next movie '{movie['title_long']}' ({next_movie}/{context['movie_count']})")
        except IndexError:
            update.callback_query.answer(text="That's it! No more movies to peek", show_alert=True)
            logger.info(f"No more movies found. Movies count: {context['movie_count']}, Requested movie index: {next_movie}")
            update.callback_query.edit_message_reply_markup(reply_markup=yts_navigator_keyboard(show_next=False))
            return

        update.callback_query.answer(text='Loading next movie from yts..')
        title, synopsis, rating, imdb, yt_trailer, image = get_minimal_movie(movie)

        movie_desc = prettify_yts_movie(title, synopsis, rating)

        # Notify that api we have succesfully handled the query
        update.callback_query.answer(text='')
        # Update current movie to next_movie
        context['movie_number'] = next_movie

        # Rebuild the same keyboard
        yts_navigator = yts_navigator_keyboard(imdb_id=imdb, yt_trailer=yt_trailer)

        photo = get_photo(image)

        if photo is None:
            bot.send_message(chat_id=update.callback_query.message.chat_id, text='Request for new photo timed out. Try again.')
            logger.info("Could not build InputMediaPhoto from url %s", image)
            return

        # Edit message photo
        bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=photo
        )
        # Edit message caption with new movie description
        update.callback_query.edit_message_caption(
            caption=movie_desc,
            reply_markup=yts_navigator
        )

    elif answer == YTS_FULL_DESC:
        update.callback_query.answer(text='Loading full description')
        movie = movies[current_movie]
        title, synopsis, rating, imdb, yt_trailer, _ = get_minimal_movie(movie, trim_description=False)
        movie_desc = prettify_yts_movie(title, synopsis, rating)
        update.callback_query.edit_message_caption(
            caption=movie_desc,
            reply_markup=yts_navigator_keyboard(imdb_id=imdb, yt_trailer=yt_trailer)
        )

    elif answer == YTS_TORRENT:
        # User chose to see torrent info
        update.callback_query.answer(text='Fetching torrent info')
        movie = movies[current_movie]
        torrents = get_torrents(movie)
        pretty_torrents = '\n'.join(prettify_torrent(movie['title_long'], torrent) for torrent in torrents)
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=pretty_torrents,
            parse_mode='markdown'
            )