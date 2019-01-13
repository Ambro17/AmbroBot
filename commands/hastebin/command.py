import logging
import os
import re

import requests

from utils.decorators import send_typing_action, log_time
from utils.utils import monospace

logger = logging.getLogger(__name__)

CODELINK_PREFIX = re.compile(r'^(@code) (?P<code>[\s\S]+)', re.IGNORECASE)


@send_typing_action
@log_time
def code_paster(bot, update, groupdict):
    code_snippet = groupdict.get('code')
    if not code_snippet:
        update.message.reply_text(f"Nop, faltó el snippet. Así: @code <snippet>")
        return

    logger.info('Posting snippet..')
    success, link = CodePaster.post_snippet(code_snippet)
    if not success:
        logger.info('Error posting snippet')
        update.message.reply_text(
            f"Che, no pude postearlo en hastebin.. Te lo pego en monospace a ver si te sirve\n"
            f"{monospace(code_snippet)}",
            parse_mode='markdown'
        )
    else:
        update.message.reply_text(link)


class CodePaster:
    URL = 'https://hastebin.com'
    ALT_URL = 'https://pastebin.com/api/api_post.php'

    @staticmethod
    def _pastebin_args(snippet):
        return {
            'api_dev_key': os.environ['PASTEBIN'],
            'api_paste_code': snippet,
            'api_option': 'paste',
            'api_paste_format': 'python',
            'api_user_key': os.environ['PASTEBIN_PRIV'],
            'api_paste_private': 2,

        }

    @classmethod
    def post_snippet_hastebin(cls, snippet):
        """Post code snippet to hastebin.

        Returns
            (bool, str): True and link if successful. False, error_msg otherwise
        """
        try:
            r = requests.post(cls.URL + '/documents', data=snippet.encode('utf-8'))
        except Exception:
            return False, f'Could not post snippet to hastebin'

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

    @classmethod
    def post_snippet_pastebin(cls, snippet):
        try:
            r = requests.post(cls.ALT_URL, data=cls._pastebin_args(snippet.encode('utf-8')))
        except Exception:
            msg = 'Error uploading snippet to pastebin.'
            logger.exception(msg)
            return False, 'Error uploading'

        if r.status_code == 200:
            return True, r.text
        else:
            return False, f'Response not ok {r.status_code} - {r.reason}'

    @classmethod
    def post_snippet(cls, snippet):
        success, msg = cls.post_snippet_hastebin(snippet)
        if not success:
            success, msg = cls.post_snippet_pastebin(snippet)

        return success, msg
