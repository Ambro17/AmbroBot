import logging
import time

from functools import wraps

import os
from telegram import ChatAction

logger = logging.getLogger(__name__)


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(bot, update, **kwargs):
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            func(bot, update, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)


def log_time(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"[{func.__name__}] <{end-start}> {kwargs if kwargs else ''}")
        return result

    return wrapped_func


def admin_only(func):
    @wraps(func)
    def restricted_func(bot, update, **kwargs):
        user = update.effective_user.username
        if user == os.environ['admin']:
            func(bot, update, **kwargs)
        else:
            logger.info("User %s not authorized to perform action.", user)

    return restricted_func
