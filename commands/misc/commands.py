import random

from telegram.ext import run_async

from utils.command_utils import monospace
from utils.constants import COMANDO_DESCONOCIDO
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
def link_ticket(bot, update, **kwargs):
    """Given a ticket id, return the url."""
    ticket_id = kwargs.get('groupdict').get('ticket')
    if ticket_id:
        bot.send_message(
            chat_id=update.message.chat_id, text=os.environ['jira'].format(ticket_id)
        )


@send_typing_action
@run_async
def default(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    bot.send_message(
        chat_id=update.message.chat_id, text=random.choice(COMANDO_DESCONOCIDO)
    )
