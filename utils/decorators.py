import logging
import time
import json

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
            return func(bot, update, **kwargs)

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
            return func(bot, update, **kwargs)
        else:
            update.message.reply_text('🚫 No estás autorizado a usar este comando')
            logger.info("User %s not authorized to perform action.", update.effective_user)

    return restricted_func


def private(func):
    @wraps(func)
    def private_func(bot, update, **kwargs):
        user_id = update.effective_user.id
        auth_users = os.environ['RETRO_USERS']
        if user_id in json.loads(auth_users):
            return func(bot, update, **kwargs)
        else:
            update.message.reply_text('🚫 No estás autorizado a usar este comando')
            logger.info("User %s not authorized to perform action.", update.effective_user)

    return private_func
