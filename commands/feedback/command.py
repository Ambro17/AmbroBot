from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from utils.utils import send_message_to_admin

SEND_FEEDBACK = 10


def default_msg(bot, update):
    update.effective_message.reply_text('Feedback message must be text. Let\'s try again with /feedback.')
    return ConversationHandler.END


def feedback(bot, update, args):
    if not args:
        update.effective_message.reply_text('Enter the bug/suggestion/feature request', quote=False)
        return SEND_FEEDBACK
    suggestion = ' '.join(args)
    _send_feedback(bot, update, suggestion)
    return ConversationHandler.END


def send_feedback(bot, update):
    suggestion = update.effective_message.text
    _send_feedback(bot, update, suggestion)
    return ConversationHandler.END


def _send_feedback(bot, update, suggestion):
    user = update.effective_message.from_user.name
    send_message_to_admin(bot, f'💬 Feedback!\n\n{suggestion}\n\nby {user}')
    update.effective_message.reply_text('✅ Feedback sent 🗳', quote=False)


feedback_receiver = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback, pass_args=True)],
    states={
        SEND_FEEDBACK: [MessageHandler(Filters.text, send_feedback)],
    },
    fallbacks=[MessageHandler(Filters.all, default_msg)],
    allow_reentry=True
)
