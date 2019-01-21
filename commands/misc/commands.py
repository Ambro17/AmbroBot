import os
import random
import re

from telegram.ext import run_async, RegexHandler, MessageHandler, Filters

from utils.utils import monospace
from utils.constants import COMANDO_DESCONOCIDO, TICKET_REGEX, CODE_PREFIX
from utils.decorators import send_typing_action, log_time


@log_time
@send_typing_action
@run_async
def format_code(bot, update, **kwargs):
    """Format text as code if it starts with $, ~, \c or \code."""
    code = kwargs.get('groupdict').get('code')
    if code:
        bot.send_message(
            chat_id=update.message.chat_id, text=monospace(code), parse_mode='markdown'
        )


@send_typing_action
@run_async
def link_ticket(bot, update):
    """Given a ticket id, return the url."""
    jira_base = os.environ['jira']
    ticket_links = '\n'.join(
        f"» {jira_base.format(match.group('ticket'))}"
        for match in re.finditer(TICKET_REGEX, update.message.text)
        )

    update.message.reply_text(ticket_links, quote=False)


@send_typing_action
@run_async
def default(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    bot.send_message(
        chat_id=update.message.chat_id, text=random.choice(COMANDO_DESCONOCIDO)
    )


code_handler = RegexHandler(CODE_PREFIX, format_code, pass_groupdict=True)
tickets_handler = MessageHandler(Filters.regex(TICKET_REGEX), link_ticket)
generic_handler = MessageHandler(Filters.command, default)
