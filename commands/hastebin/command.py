import logging
import re

import requests

from utils.utils import monospace

logger = logging.getLogger(__name__)

HASTEBIN_PREFIX = re.compile(r'^(@code) (?P<code>[\s\S]+)', re.IGNORECASE)


def hastebin(bot, update, groupdict):
    code_snippet = groupdict.get('code')
    if not code_snippet:
        update.message.reply_text(f"Nop, faltó el snippet. Así: @code <snippet>")
        return

    success, link = Hastebin.post_snippet(code_snippet)
    if not success:
        update.message.reply_text(
            f"Che, no pude postearlo en hastebin.. Te lo pego en monospace a ver si te sirve\n"
            f"{monospace(code_snippet)}",
            parse_mode='markdown'
        )
    else:
        update.message.reply_text(link)


class Hastebin:
    URL = 'https://hastebin.com'

    @classmethod
    def post_snippet(cls, snippet):
        """Post code snippet to hastebin.

        Returns
            (bool, str): Success flag and link if successful, None otherwise
        """
        try:
            r = requests.post(cls.URL + '/documents', data=snippet.encode('utf-8'))
        except Exception:
            msg = 'Error uploading snippet to hastebin'
            logger.exception(msg)
            return False, f'Exception when trying to post to {cls.URL}/documents with args {snippet}'

        if r.status_code == 200:
            try:
                return True, f"{cls.URL}/{r.json()['key']}"

            except KeyError:
                return False, f'json response did not include snippet key {r.json()}'

            except Exception:
                msg = f'Unknown error building link {r.url}'
                logger.exception(msg)
                return False, msg
        else:
            return False, f'Response not ok {r.status_code} - {r.reason}'
