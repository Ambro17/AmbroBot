from telegram.ext import run_async

from updater import elbot
from utils.decorators import send_typing_action


@elbot.command(command='remind')
@send_typing_action
@run_async
def remind(bot, update):
    # Save what the bot should remind the user
    update.message.reply_text('Talk to my friend @RRemindersBot to set reminders')
