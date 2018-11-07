#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import locale
import random
from datetime import timedelta

import dateparser
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton as Button)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PARSE_HORARIO, SET_MEETING_JOB, LOCATION, BIO = range(4)


time_delta_map = {
    'Weekly': timedelta(seconds=10),
    'Biweekly': timedelta(weeks=2),
    'Monthly': timedelta(weeks=3),
}

friendly_name = {
    'Weekly': 'semanalmente',
    'Biweekly': 'cada dos semanas',
    'Monthly': 'cada mes',
}

CANCEL = 'cancel'


def repeat_interval_keyboard():
    buttons = [
        [
            Button('Semanalmente', callback_data="Weekly"),
            Button('Bisemanalmente', callback_data="Biweekly"),
            Button('Mensualmente', callback_data="Monthly"),
        ],
        [
            Button('🚫 Cancel', callback_data=CANCEL)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def send_notification(bot, job):
    logger.info("Sending notification.")
    emoji = random.choice("📢📣🔈🔉🔊💬🎉🎊")
    bot.send_message(
        chat_id=job.context['chat_id'],
        text=f"{emoji} Reunión: {job.context['name']}! @all "
    )


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("707124089:AAELx3FtdrZYjKz0VfLNtFueP--EneCYLbw")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('m', set_meeting, pass_chat_data=True, pass_args=True)],

        states={
            PARSE_HORARIO: [MessageHandler(Filters.text, set_date, pass_chat_data=True)],

            SET_MEETING_JOB: [CallbackQueryHandler(set_meeting_job, pass_chat_data=True, pass_job_queue=True),
                              CommandHandler('cancel', cancel)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()


def set_meeting(bot, update, chat_data, args):
    logger.info("[set_meeting] Waiting for user input for meeting date.")

    if not args:
        update.message.reply_text(
            'Faltó el nombre de la reunión. `/meeting secreta`',
            parse_mode='markdown'
        )
        return

    chat_data['name'] = ' '.join(args)
    chat_data['chat_id'] = update.effective_chat.id
    update.message.reply_text(
        "📅 Elegí el día y horario de la reunión.\n"
        "Podés poner algo como `Lunes 21/07 8:45` y te voy a entender.",
        parse_mode='markdown'
    )
    return PARSE_HORARIO


def set_date(bot, update, chat_data):
    logger.info("[set_date] Parsing user input into a meeting date.")
    locale.setlocale(locale.LC_TIME, "es_AR.utf8")
    date_obj = dateparser.parse(update.message.text)
    if not date_obj:
        update.message.reply_text(
            "No pude interpretar la fecha. Volvé a intentar con un formato más estándar."
        )
        return

    logger.info("[set_date] Parsed date : %s", date_obj)

    date_string = date_obj.strftime('%A %d/%m %H:%M')
    chat_data['date'] = date_string
    chat_data['datetime'] = date_obj
    logger.info(f"[set_date] Horario elegido. {date_string}")

    update.message.reply_text(
        f'Perfecto, la próxima reunión será el: `{date_string.capitalize()}`\n'
        'Cada cuanto se va a repetir esta reunión?',
        parse_mode='markdown',
        reply_markup=repeat_interval_keyboard()
    )

    return SET_MEETING_JOB




def set_meeting_job(bot, update, chat_data, job_queue):
    logger.info("[set_meeting_job] Setting cron job of meeting.")

    if update.callback_query.data == CANCEL:
        update.callback_query.answer(text='')
        update.effective_message.edit_text('Meeting cancelada! Vuelva prontos')
        logger.info("Conversation ended.")
        return ConversationHandler.END

    time_delta = time_delta_map[update.callback_query.data]
    frequency_friendly_name = friendly_name[update.callback_query.data]

    job_queue.run_repeating(
        send_notification,
        interval=time_delta,
        first=chat_data['datetime'],
        context=chat_data
    )
    logger.info("[set_meeting_job] Meeting set with datetime %s and timedelta %s.", chat_data['datetime'], time_delta)

    update.callback_query.answer(text='Meeting saved')
    # Feature: manage jobs in db to survive bot shutdown
    update.callback_query.message.edit_text(
        f"✅ Listo. La reunión '{chat_data['name']}' quedó seteada para el  `{chat_data['date'].capitalize()}` "
        f"y se repetirá {frequency_friendly_name}",
        parse_mode='markdown',
        reply_markup=None
    )

    logger.info("Conversation has ended.")
    return ConversationHandler.END


if __name__ == '__main__':
    main()
