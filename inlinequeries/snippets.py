#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from functools import partial

from Levenshtein._levenshtein import jaro_winkler

from telegram import (
    InlineQueryResultArticle,
    ParseMode,
    InputTextMessageContent
)
from telegram.ext import InlineQueryHandler
import logging

from telegram.utils.helpers import escape_markdown

from commands.snippets.utils import select_all_snippets
from utils.constants import MINUTE
from utils.decorators import requires_auth, inline_auth

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def _article(id, title, text, parse_mode=ParseMode.MARKDOWN):
    reply_text = f"*» {title}*\n{escape_markdown(text)}"
    try:
        msg = InputTextMessageContent(reply_text, parse_mode=parse_mode)
    except Exception:
        logger.error(text)
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
def inlinequery(bot, update, chat_data):
    """Show all snippets if query is empty string or filter by string similarity"""
    user_input = update.inline_query.query

    # Cache for 5 minutes in chat_data.
    snippets = chat_data.get('snippets')
    if not snippets or (chat_data.get('last_update', 0) - time.time()) > 5 * MINUTE:
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


inline_snippets = InlineQueryHandler(inlinequery, pass_chat_data=True)
