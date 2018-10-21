import logging

from callbacks.command_callbacks import dolarhoy_callback, peliculas_callback, hoypido_callback
from command.serie.constants import LOAD_EPISODES, LATEST_EPISODES, GO_BACK_TO_MAIN, SEASON_T, EPISODE_T
from command.serie.utils import (
    get_torrents_by_id,
    prettify_serie,
    get_all_seasons,
    prettify_episodes,
    prettify_torrents,
)
from keyboards.keyboards import banco_keyboard, pelis_keyboard, hoypido_keyboard, serie_keyboard, \
    serie_go_back_keyboard, serie_season_keyboard, serie_episodes_keyboards

logger = logging.getLogger(__name__)

command_callback = {
    'dolarhoy': dolarhoy_callback,
    'pelicula': peliculas_callback,
    'hoypido': hoypido_callback,
}


def handle_callbacks(bot, update, chat_data):
    # Get the handler based on the command
    context = chat_data.get('context')
    if not context:
        message = f"Ups.. 😳 no pude encontrar lo que me pediste.\n" \
                  f"Podés probar invocando de nuevo el comando a ver si me sale 😊"
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode='markdown'
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    # Get user selection
    answer = update.callback_query.data

    callback_handler = command_callback[context['command']]

    # Get the relevant info based on user choice
    handled_response = callback_handler(context['data'], answer)
    # Notify that api we have succesfully handled the query
    update.callback_query.answer(text='')

    # Rebuild the same keyboard
    if context['command'] == 'dolarhoy':
        keyboard = banco_keyboard()
    elif context['command'] == 'pelicula':
        keyboard = pelis_keyboard()
    else:
        keyboard = hoypido_keyboard()

    if context.get('edit_original_text'):
        update.callback_query.edit_message_text(
            text=handled_response, reply_markup=keyboard, parse_mode='markdown'
        )
    else:
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=handled_response,
            parse_mode='markdown'
        )


def serie_callback_handler(bot, update, chat_data):
    context = chat_data.get('context')
    if not context:
        message = f"Ups.. 😳 no pude encontrar lo que me pediste.\n" \
                  f"Podés probar invocando de nuevo el comando a ver si me sale 😊"
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode='markdown'
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    # Get user selection
    answer = update.callback_query.data
    if answer == LATEST_EPISODES:
        # Get latest episodes from eztv api
        update.callback_query.answer(text='Getting latest episodes..')
        keyboard = serie_go_back_keyboard()
        imdb_id = context['data']['imdb_id']
        torrents = get_torrents_by_id(imdb_id)

        if not torrents:
            message = ("Eztv api did not return any result for the series. ❕\nPlease notice it's still in beta mode. 🐣\n"
                       "You can try loading all episodes and manually searching the latest.")
            update.callback_query.edit_message_text(
                text=message,
                reply_markup=keyboard,
            )
            return

        pretty_torrents = prettify_torrents(torrents)
        response = pretty_torrents if pretty_torrents else 'eztv api failed to respond with latest torrents'

    elif answer == GO_BACK_TO_MAIN:
        # Remove season and episode context so we can start the search again if the user wants to download another episode.
        context.pop('selected_season_episodes', None)

        # Resend series basic description
        message = context['data']['message_info']
        response = prettify_serie(*message)
        keyboard = serie_keyboard()
        # tothink: Maybe implement relative go back. chat_data context should be more intelligent to support that.
        # temp key on chat_data (active_season) that resets after each episode go back?

    elif answer == LOAD_EPISODES:
        # Load all episodes parsing eztv web page
        # They should be loaded by now but just in case.
        seasons = chat_data['context'].get('seasons')
        if not seasons:
            update.callback_query.answer(text='Loading episodes.. this may take a while')
            seasons = chat_data['context']['seasons'] = get_all_seasons(context['data']['series_name'])

        response = 'Choose a season to see its episodes.'
        keyboard = serie_season_keyboard(seasons)

    elif answer.startswith(SEASON_T.format('')):
        season_choice = answer.split('_')[-1]
        update.callback_query.answer(text=f'Loading episodes from season {season_choice}')
        season_episodes = chat_data['context']['seasons'][int(season_choice)]
        chat_data['context']['selected_season_episodes'] = season_episodes
        response = f'You chose season {season_choice}.'
        logger.info(f"Season %s episodes %s", season_choice, tuple(season_episodes.keys()))
        keyboard = serie_episodes_keyboards(season_episodes)

    elif answer.startswith(EPISODE_T.format('')):
        episode = answer.split('_')[-1]
        update.callback_query.answer(text=f'Loading torrents of episode {episode}')
        episode_list = chat_data['context']['selected_season_episodes'][int(episode)]
        the_episodes = prettify_episodes(episode_list)
        response = the_episodes if the_episodes else 'No episodes found.'
        keyboard = serie_go_back_keyboard()
    else:
        keyboard = serie_go_back_keyboard()
        response = 'Unknown button %s' % answer
        logger.info("We shouldn't be here. chat_data=%s, answer=%s", chat_data, answer)

    update.callback_query.answer(text='')

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode='markdown'
        )
    else:
        logger.info("Selected option '%s' would leave text as it is. Ignoring to avoid exception. '%s' " % (answer, response))
