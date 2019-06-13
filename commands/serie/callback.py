import logging

from telegram.ext import CallbackQueryHandler

from commands.serie.constants import (
    LOAD_EPISODES,
    LATEST_EPISODES,
    GO_BACK_TO_MAIN,
    SEASON_T,
    EPISODE_T,
    EZTV_API_ERROR,
    EZTV_NO_RESULTS,
    LOAD_MORE_LATEST,
    SERIE_REGEX)
from commands.serie.keyboard import (
    serie_go_back_keyboard,
    serie_episodes_keyboards,
    serie_season_keyboard,
    serie_main_keyboard,
    serie_load_more_latest_episodes_keyboard,
)
from commands.serie.utils import (
    request_eztv_torrents_by_imdb_id,
    prettify_serie,
    get_all_seasons,
    prettify_episodes,
    prettify_torrents,
)
from updater import elbot

logger = logging.getLogger(__name__)


@elbot.callbackquery(pattern=SERIE_REGEX, pass_chat_data=True)
def serie_callback_handler(bot, update, chat_data):
    context = chat_data.get('context')
    if not context:
        message = (
            f"Ouch, no pude responder a tu pedido.\n"
            f"Probá invocando de nuevo el comando a ver si me sale 😊"
        )
        logger.info(f"Conflicting update: '{update.to_dict()}'. Chat data: {chat_data}")
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message,
            parse_mode='markdown',
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    # Get user selection
    answer = update.callback_query.data
    if answer == LATEST_EPISODES:
        # Get latest episodes from eztv api
        logger.info("User chose latest episodes")
        update.callback_query.answer(text='Getting latest episodes.. Please be patient')
        imdb_id = context['data']['imdb_id']
        context['data']['torrents'] = torrents = request_eztv_torrents_by_imdb_id(imdb_id)

        if not torrents:
            logger.info(f"No torrents for {context['data']['series_name']}")
            update.callback_query.edit_message_text(
                text=EZTV_NO_RESULTS, reply_markup=serie_go_back_keyboard()
            )
            return

        # Show only the first (latest) 5 torrents
        response = prettify_torrents(torrents, limit=5)
        keyboard = serie_load_more_latest_episodes_keyboard()

    elif answer == LOAD_MORE_LATEST:
        # Load all episodes from api
        response = prettify_torrents(context['data']['torrents'], limit=None)
        keyboard = serie_go_back_keyboard()
        # Todo, do further requests to show all api results. Maybe paging results into numbers?

    elif answer == GO_BACK_TO_MAIN:
        # Remove season and episode context so we can start the search again
        # if the user wants to download another episode.
        context.pop('selected_season_episodes', None)

        # Resend series basic description
        message = context['data']['message_info']
        response = prettify_serie(*message)
        keyboard = serie_main_keyboard(context['data']['imdb_id'])
        # tothink: Maybe implement relative go back. chat_data context
        # should be more intelligent to support that.
        # temp key on chat_data (active_season) that resets after each episode go back?

    elif answer == LOAD_EPISODES:
        # Load all episodes parsing eztv web page
        # They should be loaded by now but just in case.
        seasons = chat_data['context'].get('seasons')
        if not seasons:
            update.callback_query.answer(
                text='Loading episodes.. this may take a while'
            )
            seasons = chat_data['context']['seasons'] = get_all_seasons(
                context['data']['series_name'], context['data']['series_raw_name']
            )

        response = 'Choose a season to see its episodes.'
        keyboard = serie_season_keyboard(seasons)

    elif answer.startswith(SEASON_T.format('')):
        season_choice = answer.split('_')[-1]
        update.callback_query.answer(
            text=f'Loading episodes from season {season_choice}'
        )
        season_episodes = chat_data['context']['seasons'][int(season_choice)]
        chat_data['context']['selected_season_episodes'] = season_episodes
        response = f'Season {season_choice}, choose an episode'
        logger.info(f"Season %s episodes %s", season_choice, sorted(tuple(season_episodes.keys())))
        keyboard = serie_episodes_keyboards(season_episodes)

    elif answer.startswith(EPISODE_T.format('')):
        episode = answer.split('_')[-1]
        update.callback_query.answer(text=f'Loading torrents of episode {episode}')
        episode_list = chat_data['context']['selected_season_episodes'][int(episode)]
        the_episodes = prettify_episodes(episode_list)
        response = the_episodes if the_episodes else 'No episodes found.'
        keyboard = serie_go_back_keyboard()
    else:
        response = 'Unknown button %s' % answer
        keyboard = serie_go_back_keyboard()
        logger.info("We shouldn't be here. chat_data=%s, answer=%s", chat_data, answer)

    update.callback_query.answer(text='')

    original_text = update.callback_query.message.text
    if response != original_text:
        update.callback_query.edit_message_text(
            text=response, reply_markup=keyboard, parse_mode='markdown'
        )
    else:
        logger.info(
            "Selected option '%s' would leave text as it is. Ignoring to avoid exception. '%s' "
            % (answer, response)
        )
