import logging
from functools import partialmethod

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    RegexHandler,
    InlineQueryHandler,
)

logger = logging.getLogger(__name__)


class HandlerMapper:
    handlers = []

    @classmethod
    def route(cls, handler_type, group=0, **handler_args):
        """Add the handler to the dispatcher by decorating a function.

        Usage:
            @dispatcher.route(command='code')
            def mycommand(bot, update):
                update.message.reply_text('You invoked /code command')
        """

        handler_mapping = {
            'command': (CommandHandler, ('command',)),
            'message': (MessageHandler, ('filters',)),
            'regex': (RegexHandler, ('pattern',)),
            'inlinequery': (InlineQueryHandler, ()),
            'callbackquery': (CallbackQueryHandler, ()),
        }

        if handler_type not in handler_mapping:
            raise ValueError('Invalid handler type. %s', handler_type)

        def decorator(func):
            handler_factory, required_args = handler_mapping[handler_type]
            if any(required_arg not in handler_args for required_arg in required_args):
                raise ValueError('Missing required arguments. %s', required_args)

            handler_args['callback'] = func
            handler = handler_factory(**handler_args)
            new_handler = {
                'handler': handler,
                'group': group,
            }
            cls.handlers.append(new_handler)
            logger.info('Added handler for %s', func.__name__)

        return decorator

    command = partialmethod(route, handler_type='command')
    message = partialmethod(route, handler_type='message')
    regex = partialmethod(route, handler_type='regex')
    callbackquery = partialmethod(route, handler_type='callbackquery')
    inlinequery = partialmethod(route, handler_type='inlinequery')


elbot = HandlerMapper