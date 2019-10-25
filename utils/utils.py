import logging
import os
import signal
import random

import requests
from bs4 import BeautifulSoup
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut
from telegram.ext import MessageHandler, Filters

from utils.constants import COMANDO_DESCONOCIDO
from utils.decorators import send_typing_action

logger = logging.getLogger(__name__)


# Generic utils
def monospace(text):
    return f'```\n{text}\n```'


def trim(text, limit=11, trim_end='.'):
    """Trim and append . if text is too long. Else return it unmodified"""
    return f'{text[:limit]}{trim_end}' if len(text) > limit else text


def soupify_url(url, timeout=2, encoding='utf-8', **kwargs):
    """Given a url returns a BeautifulSoup object"""
    try:
        r = requests.get(url, timeout=timeout, **kwargs)
    except requests.ReadTimeout:
        logger.info("[soupify_url] Request for %s timed out.", url)
        raise
    except Exception as e:
        logger.error(f"Request for {url} could not be resolved", exc_info=True)
        raise ConnectionError(repr(e))

    r.raise_for_status()
    r.encoding = encoding
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'lxml')
    else:
        raise ConnectionError(
            f'{url} returned error status %s - ', r.status_code, r.reason
        )


def error_handler(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.info("User unauthorized")
    except BadRequest as e:
        msg = getattr(error, 'message', None)
        if msg is None:
            raise
        if msg == 'Query_id_invalid':
            logger.info("We took too long to answer.")
        elif 'Message is not modified' in msg:
            logger.info(
                "Tried to edit a message but text hasn't changed."
                " Probably a button in inline keyboard was pressed but it didn't change the message"
            )
        else:
            logger.info("Bad Request exception: %s", msg)

    except TimedOut:
        logger.info("Request timed out")
        bot.send_message(
            chat_id=update.effective_message.chat_id, text='The request timed out ⌛️'
        )

    except TelegramError:
        logger.exception("A TelegramError occurred")

    finally:
        try:
            text = update.effective_message.text
            user = update.effective_user.name
            chat = update.effective_chat

            error_msg = (f"User: {user}\nText: {text}\n"
                         f"Chat: {chat.id, chat.type, chat.username}\n"
                         f"Error: {repr(error)} - {str(error)}")

            logger.info(f"Conflicting update: {error_msg}")

        except Exception:
            error_msg = f'Error found: {error}. Update: {update}'
            logger.error(error_msg, exc_info=True)

        if 'Message is not modified' not in error_msg:
            send_message_to_admin(bot, error_msg)


def send_message_to_admin(bot, message, **kwargs):
    bot.send_message(chat_id=os.environ['ADMIN_ID'], text=message, **kwargs)


def signal_handler(signal_number, frame):
    sig_name = signal.Signals(signal_number).name
    logger.info(f'Captured signal number {signal_number}. Name: {sig_name}')


@send_typing_action
def unknown_command(bot, update):
    """If a user sends an unknown command, answer accordingly"""
    update.message.reply_text(random.choice(COMANDO_DESCONOCIDO))


unknown_commands = MessageHandler(Filters.command, unknown_command)
