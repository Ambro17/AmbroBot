import os
import random
import re

from telegram.ext import run_async, RegexHandler, MessageHandler, Filters, CommandHandler

from updater import elbot
from utils.utils import monospace
from utils.constants import COMANDO_DESCONOCIDO, TICKET_REGEX, CODE_PREFIX
from utils.decorators import send_typing_action, log_time


@log_time
@send_typing_action
@elbot.regex(pattern=CODE_PREFIX, pass_groupdict=True)
def format_code(bot, update, groupdict):
    """Format text as code if it starts with $, ~, \c or \code."""
    code = groupdict.get('code')
    if code:
        update.message.reply_text(
            monospace(code), parse_mode='markdown'
        )


@send_typing_action
@run_async
@elbot.message(filters=Filters.regex(TICKET_REGEX))
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
@elbot.route(command='code')
def code(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    REPO = 'https://github.com/Ambro17/AmbroBot'
    msg = (
        f"Here you can see my internals: {REPO}\n"
        "Don't forget to give it a ⭐️ if you like it!"
    )
    update.message.reply_text(msg, disable_web_page_preview=True)
