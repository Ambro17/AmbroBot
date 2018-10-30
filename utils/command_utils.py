import logging
from telegram.error import (
    TelegramError,
    Unauthorized,
    BadRequest,
    TimedOut)
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache


logger = logging.getLogger(__name__)


# Generic utils
def monospace(text):
    return f'```\n{text}\n```'


def normalize(text, limit=11, trim_end='.'):
    """Trim and append . if text is too long. Else return it unmodified"""
    return f'{text[:limit]}{trim_end}' if len(text) > limit else text


class Soupifier(object):
    """Implements a cache with expiration for the given urls.

    Each url is a key of the cache dict. Its value is the soupified url.
    During n minutes, the value will be remembered, after that it will be
    removed and the request will happen again
    """

    def __init__(self, minutes_to_live=5, timeout=2):
        self.cache = TTLCache(maxsize=10, ttl=60 * minutes_to_live)
        self.timeout = timeout

    def soupify(self, url):
        try:
            soup = self.cache[url]
            logger.info("Cached value for %s", url)
            return soup
        except KeyError:
            logger.info("Caché for %s expired. Updating.", url)
            self.cache[url] = soupify_url(url, timeout=self.timeout)
            return self.cache[url]


# To be used after profiling bot use
soup = Soupifier()
_soupify_url = soup.soupify


def soupify_url(url, timeout=2, encoding='utf-8'):
    """Given a url returns a BeautifulSoup object"""
    r = requests.get(url, timeout=timeout)
    r.encoding = encoding
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'lxml')
    else:
        raise ConnectionError(f'{url} did not respond.')


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
        elif msg == 'Message is not modified':
            logger.info("Tried to edit a message but text hasn't changed."
                        " Probably a button in inline keyboard was pressed but it didn't change the message")
        else:
            logger.info("Bad Request exception: %s", msg)

    except TimedOut:
        logger.info("Request timed out")
        bot.send_message(chat_id=update.effective_message.chat_id, text='The request timed out ⌛️')

    except TelegramError:
        logger.exception("A TelegramError occurred")

    finally:
        logger.info(f"Conflicting update: '{update.to_dict()}'")