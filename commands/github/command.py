from telegram.ext import CommandHandler


def github_repo(bot, update):
    update.message.reply_text('You can find my source code @ https://github.com/Ambro17/AmbroBot')


github_handler = CommandHandler('github', github_repo)
