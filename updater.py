import os
from functools import partialmethod

from telegram.ext import (
    Updater,
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    RegexHandler,
    InlineQueryHandler,
)
from utils.utils import signal_handler


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

        return decorator

    command = partialmethod(route, handler_type='command')
    message = partialmethod(route, handler_type='message')
    regex = partialmethod(route, handler_type='regex')
    callbackquery = partialmethod(route, handler_type='callbackquery')
    inlinequery = partialmethod(route, handler_type='inlinequery')


elbot = HandlerMapper

#
# class TheDispatcher(Dispatcher):
#     """Dispatcher with decorator to map functions to handlers"""
#
#     def route(self, handler_type='command', group=0, **handler_args):
#         """Add the handler to the dispatcher by decorating a function.
#
#         Usage:
#             @dispatcher.route(command='code')
#             def mycommand(bot, update):
#                 update.message.reply_text('You invoked /code command')
#         """
#
#         handlers = {
#             'command': (CommandHandler, ('command',)),
#             'message': (MessageHandler, ('filters',)),
#             'regex': (RegexHandler, ('pattern',)),
#             'inlinequery': (InlineQueryHandler, ()),
#             'callbackquery': (CallbackQueryHandler, ()),
#         }
#
#         def decorator(func):
#             if handler_type not in handlers:
#                 raise ValueError('Invalid handler type. %s' % handler_type)
#
#             handler_factory, required_args = handlers[handler_type]
#             if any(req_arg not in handler_args for req_arg in required_args):
#                 raise ValueError('Missing required arguments. %s' % required_args)
#
#             handler_args['callback'] = func
#             handler = handler_factory(**handler_args)
#             self.add_handler(handler, group=group)
#
#         return decorator
#
#     command = partialmethod(route, handler_type='command')
#     message = partialmethod(route, handler_type='message')
#     regex = partialmethod(route, handler_type='regex')
#     callbackquery = partialmethod(route, handler_type='callbackquery')
#     inlinequery = partialmethod(route, handler_type='inlinequery')
#
#
# class TheUpdater(Updater):
#     """Updater with support for dispatcher with extra functionality"""
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.dispatcher = TheDispatcher(
#             self.bot,
#             self.update_queue,
#             job_queue=self.job_queue,
#         )
#
#
# # Expose the bot to the outer world.
# updater = TheUpdater(os.environ['PYTEL'], user_sig_handler=signal_handler)
# elbot = updater.dispatcher
