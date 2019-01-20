import os
import json
import logging
import time
import inspect
from functools import wraps

import telegram
from telegram import ChatAction

from commands.register.db import authorized_user

logger = logging.getLogger(__name__)


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(bot, update, **kwargs):
            bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            return func(bot, update, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
send_recording_action = send_action(ChatAction.RECORD_AUDIO)
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
            logger.info("User %s not authorized to perform action.", user)

    return restricted_func


def group_only(func):
    # Ignore action if it doesn't happen on allowed group
    @wraps(func)
    def restricted_func(bot, update, **kwargs):
        id = update.effective_user.id
        if id in json.loads(os.environ['RETRO_USERS']):
            return func(bot, update, **kwargs)
        else:
            update.message.reply_text('🚫 No estás autorizado a usar este comando')
            logger.info(
                "User %s not authorized to perform action.", update.effective_user
            )

    return restricted_func


def handle_empty_arg(*, required_params, error_message='Faltó un argumento', parse_mode=None):
    """Shortcut function execution if any of the required_params is empty.

    This decorator was created because many commands should output an error message if a
    required argument was supplied with a empty value. By defining this decorator, we can
    better follow the DRY principle, by parametrizing what message will be shown if certain
    required parameters are empty.

    For example /serie must be supplied with a <series name>. So if a user calls /serie without
    any series_name, `error_message` will be replied on that conversation

    All decorated functions are expected to have a signature of a telegram bot callback. Namely:
        >>> def callback(bot, update, optional_arg_1, optional_arg_2, ... )
    A toy example would be:
        >>> @handle_empty_arg('req_param')
        >>> def test(bot, update, req_param, a, b)
                pass
        >>>test(bot, update, '', 'a', 'b')
        [Out] 'Faltó un argumento'

    """

    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            argument_and_values = zip(inspect.signature(func).parameters, args + tuple(kwargs.values()))
            required_arg_is_empty = any(
                not value
                for arg, value in argument_and_values
                if arg in required_params
            )
            if required_arg_is_empty:
                bot, update, *remainder = args
                return update.effective_message.reply_text(error_message, parse_mode=parse_mode)
            else:
                return func(*args, **kwargs)

        return wrapped_func

    return decorator


def requires_auth(func):
    """Decorate functions to prevent usage by unregistered users."""
    @wraps(func)
    def restricted_func(bot, update, **kwargs):
        user_id = update.effective_user.id
        if authorized_user(user_id):
            return func(bot, update, **kwargs)
        else:
            logger.info(f"{update.effective_user.name} (id={user_id})"
                        f" wants to execute {update.effective_message.text}")
            update.effective_message.reply_text(
                'Debés registrarte primero para usar este comando. Escribí `/register`',
                parse_mode='markdown',
                quote=False
            )

    return restricted_func


def inline_auth(func):
    """Allow only authorized users to user the decorated funcs"""

    @wraps(func)
    def restricted_func(bot, update, **kwargs):
        user_id = update.effective_user.id
        if authorized_user(user_id):
            return func(bot, update, **kwargs)
        else:
            logger.info(f"{update.effective_user.name} (id={user_id})"
                        f" wants to inlinequery with '{update.inline_query.query}'")
            bot.send_message(
                chat_id=user_id,
                text='🚫 Access denied. Write `/register` to register',
                parse_mode='markdown',
                quote=False
            )

    return restricted_func


def private_chat_only(func):
    @wraps(func)
    def deco_func(bot, update, **kwargs):
        chat_type = update.effective_chat.type
        if chat_type == telegram.Chat.PRIVATE:
            return func(bot, update, **kwargs)
        else:
            logger.info(f"{update.effective_message.text} can only be executed on a private conversation."
                        f" {update.effective_user.name}")
            update.effective_message.reply_text(
                'El comando funciona solo en conversacion privada con @CuervoBot.\n'
                'Clickea el username para iniciar una conversación con él',
                parse_mode='markdown',
                quote=False
            )

    return deco_func
