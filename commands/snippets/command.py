# -*- coding: UTF-8 -*-
import logging
import time
from functools import partial

from Levenshtein._levenshtein import jaro_winkler
from telegram import ParseMode, InputTextMessageContent, InlineQueryResultArticle
from telegram.ext import run_async
from telegram.utils.helpers import escape_markdown

from commands.snippets.constants import SAVE_REGEX, GET_REGEX, DELETE_REGEX
from commands.snippets.utils import (
    lookup_content,
    save_to_db,
    select_all_snippets,
    remove_snippet,
    link_key)
from updater import elbot
from utils.constants import MINUTE
from utils.decorators import send_typing_action, log_time, admin_only, requires_auth, inline_auth

logger = logging.getLogger(__name__)


@log_time
@send_typing_action
@run_async
@requires_auth
@elbot.route(handler_type='regex', pattern=SAVE_REGEX, pass_groupdict=True)
def save_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = kwargs['groupdict'].get('content')

    if None in (key, content):
        message = 'No respetaste el formato. Intentá de nuevo'
    else:
        sucess, error_message = save_to_db(key, content)
        if sucess:
            message = f'Info guardada ✅.\nPodés leerla escribiendo `@get {key}`'
        else:
            message = error_message.format(key)

    bot.send_message(
        chat_id=update.message.chat_id, text=message, parse_mode='markdown'
    )


@log_time
@send_typing_action
@run_async
@requires_auth
@elbot.route(handler_type='regex', pattern=GET_REGEX, pass_groupdict=True)
def get_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = lookup_content(key)
    if content:
        key, saved_data = content
        bot.send_message(chat_id=update.message.chat_id, text=saved_data)
    else:
        message = f"No hay nada guardado bajo '{key}'.\nProbá /snippets para ver qué datos están guardados"
        bot.send_message(chat_id=update.message.chat_id, text=message)


@log_time
@send_typing_action
@run_async
@requires_auth
@elbot.route(command='get', pass_args=True)
def get_snippet_command(bot, update, args):
    """Duplicate of get_snippet because only /commands can be clickable."""
    if not args:
        update.message.reply_text('Faltó poner la clave `/get <clave>`', parse_mode='markdown')
        return
    key = ' '.join(args)
    content = lookup_content(key)
    if content:
        key, saved_data = content
        bot.send_message(chat_id=update.message.chat_id, text=saved_data)
    else:
        message = f"No hay nada guardado bajo '{key}'.\nProbá /snippets para ver qué datos están guardados"
        bot.send_message(chat_id=update.message.chat_id, text=message)


@log_time
@send_typing_action
@run_async
@requires_auth
@elbot.route(command='snippets')
def show_snippets(bot, update):
    answers = select_all_snippets()
    if answers:
        keys = [f'🔑  {link_key(key)}' for id, key, content in answers]
        reminder = ['Para ver algún snippet » `/get <clave>` o\nclickeá la clave y reenviá a un chat donde esté yo']
        update.message.reply_text(text='\n\n'.join(keys + reminder), parse_mode='markdown')
    else:
        update.message.reply_text(
            'No hay ningún snippet guardado!\nPodés empezar usando `#key snippet_to_save`',
            parse_mode='markdown',
        )


@run_async
@log_time
@admin_only
@elbot.route(handler_type='regex', pattern=DELETE_REGEX, pass_groupdict=True)
def delete_snippet(bot, update, groupdict):
    key = groupdict.get('key')
    if not key:
        update.message.reply_text('Te faltó poner qué snippet borrar')
        return

    removed = remove_snippet(key)
    if removed:
        message = f"✅ El snippet `{key}` fue borrado"
    else:
        message = 'No se pudo borrar la pregunta.'

    update.message.reply_text(message, parse_mode='markdown')


def _article(id, title, text, parse_mode=ParseMode.MARKDOWN):
    reply_text = f"*» {title}*\n{escape_markdown(text)}"
    try:
        msg = InputTextMessageContent(reply_text, parse_mode=parse_mode)
    except Exception:
        logger.error(text)
        raise
    return InlineQueryResultArticle(
        id=id,
        title=f'{title}',
        description='Code snippets',
        input_message_content=msg,
    )


def is_similar(a, b, tolerance=0.58):
    similarity = jaro_winkler(a.lower(), b.lower())
    return similarity > tolerance


def _filter_snippets(snippets, filter_f):
    return [
        _article(id, snippet_key, content)
        for id, snippet_key, content in snippets if filter_f(snippet_key)
    ]


@inline_auth
@elbot.route(handler_type='inlinequery', pass_chat_data=True)
def inlinequery(bot, update, chat_data):
    """Show all snippets if query is empty string or filter by string similarity"""
    user_input = update.inline_query.query

    # Cache for 5 minutes in chat_data.
    snippets = chat_data.get('snippets')
    if not snippets or (chat_data.get('last_update', 0) - time.time()) > 1 * MINUTE:
        chat_data['snippets'] = snippets = select_all_snippets()
        logger.info('Recaching snippets')

    logger.info(f'Snippets: {len(snippets)}')

    if not snippets:
        return
    if len(user_input) == 0:
        results = _filter_snippets(snippets, lambda s: True)
    else:
        results = _filter_snippets(snippets, partial(is_similar, user_input.lower(), tolerance=0.58))
        logger.info(f"Filtered results: {len(results)} by '{user_input}'")

    update.inline_query.answer(results, cache_time=0)
    chat_data['last_update'] = time.time()
