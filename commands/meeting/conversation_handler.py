import random
from datetime import datetime as d, timezone, timedelta

import dateparser
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    run_async)

import logging

from commands.meeting.constants import MEETING_FILTER, CANCEL, time_delta_map
from commands.meeting.keyboard import repeat_interval_keyboard
from commands.meeting.db_operations import save_meeting
from utils.constants import GMT_BUENOS_AIRES
from utils.decorators import group_only, send_typing_action, log_time

logger = logging.getLogger(__name__)

PARSE_HORARIO, SET_MEETING_JOB = range(2)

friendly_name = {
    'Weekly': 'semanalmente',
    'Biweekly': 'cada dos semanas',
    'Monthly': 'cada mes',
}


# Entry point
@log_time
@send_typing_action
@run_async
@group_only
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


# First state
def set_date(bot, update, chat_data):
    logger.info("[set_date] Parsing user input into a meeting date.")
    date_obj = dateparser.parse(update.message.text, settings={'PREFER_DATES_FROM': 'future'})
    logger.info("[set_date] Raw naive user date %s", date_obj)
    # Users are from argentina but server is hosted on US. So we must clarify that 17:00 means 17:00 in UTC-3
    buenos_aires_offset = timezone(timedelta(hours=GMT_BUENOS_AIRES))
    date_obj = date_obj.replace(tzinfo=buenos_aires_offset)
    logger.info("[set_date] timezone aware user date %s.", date_obj)
    if not date_obj:
        logger.info("[set_date] Error detecting date from user string")
        update.message.reply_text(
            "No pude interpretar la fecha. Volvé a intentar con un formato más estándar."
        )
        return
    elif date_obj < d.now(buenos_aires_offset):
        logger.info("[set_date] Date can't be earlier than current time.")
        update.message.reply_text(
            "La fecha debe ser una fecha futura.\nLos viajes en el tiempo aún no están soportados.\n"
            "Intentá de nuevo"
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


# Second state
def set_meeting_job(bot, update, chat_data, job_queue):
    logger.info("[set_meeting_job] Setting cron job of meeting.")

    if update.callback_query.data == CANCEL:
        update.callback_query.answer(text='')
        update.effective_message.edit_text('Meeting cancelada ⛔️')
        logger.info("Conversation ended.")
        return ConversationHandler.END

    period_key = update.callback_query.data.split('_')[-1]
    time_delta = time_delta_map[period_key]
    frequency_friendly_name = friendly_name[period_key]

    # Feature: manage jobs in db to survive bot shutdown
    job_queue.run_repeating(
        send_notification,
        interval=time_delta,
        first=chat_data['datetime'],
        context=chat_data
    )
    logger.info("[set_meeting_job] Meeting set with datetime %s and timedelta %s.", chat_data['datetime'], time_delta)

    # Save meeting to db
    try:
        save_meeting(chat_data['name'], chat_data['datetime'])
    except Exception:
        logger.exception("Meeting could not be saved")

    update.callback_query.answer(text='Meeting saved')
    update.callback_query.message.edit_text(
        f"✅ Listo. La reunión `{chat_data['name']}` quedó seteada para el  `{chat_data['date'].capitalize()}` "
        f"y se repetirá `{frequency_friendly_name}`",
        parse_mode='markdown',
        reply_markup=None
    )

    logger.info("Conversation has ended.")
    return ConversationHandler.END


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


def default_msg(bot, update):
    update.effective_message.reply_text('Sabés que no te entendí. Empecemos de nuevo.')
    return ConversationHandler.END


def default(bot, update):
    update.callback_query.answer(text='')
    update.callback_query.message.edit_text(
        '🤕 Algo me confundió. Podemos empezar de nuevo con /meeting',
        reply_markup=None,
    )
    return ConversationHandler.END


meeting_conversation = ConversationHandler(
    entry_points=[
        CommandHandler('meeting', set_meeting, pass_chat_data=True, pass_args=True)
    ],
    states={
        PARSE_HORARIO: [MessageHandler(Filters.text, set_date, pass_chat_data=True)],

        SET_MEETING_JOB: [
            CallbackQueryHandler(set_meeting_job, pattern=MEETING_FILTER, pass_chat_data=True, pass_job_queue=True),
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, default_msg),
        CallbackQueryHandler(default)
    ],
    allow_reentry=True
)
