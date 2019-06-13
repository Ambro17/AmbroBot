from telegram.ext import run_async, CommandHandler

from updater import elbot
from utils.decorators import send_typing_action


@send_typing_action
@run_async
@elbot.command(command='remind', pass_chat_data=True)
def remind(bot, update):
    # Save what the bot should remind the user
    update.message.reply_text('Talk to my friend @RRemindersBot to set reminders')
