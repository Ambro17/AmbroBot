import copy
from datetime import datetime, timedelta
import logging

import pytz
from telegram.ext import run_async

from commands.remindme.constants import REMINDER_DEFAULT, MISSING_CHAT_DATA, BUENOS_AIRES_TIMEZONE
from commands.remindme.job import send_notification
from commands.remindme.keyboards import time_options_keyboard
from commands.remindme.utils import get_delay, _tag_user, _datetime_from_answer, add_job_to_db
from utils.decorators import send_typing_action, log_time
from utils.utils import send_message_to_admin

logger = logging.getLogger(__name__)


@send_typing_action
@run_async
def remind(bot, update, chat_data, args):
    # Save what the bot should remind the user
    user = update.message.from_user
    thing_to_remind = ' '.join(args)
    context = {
        'thing_to_remind': thing_to_remind,
        'user_id': user.id,
        'user_tag': _tag_user(user),
        'chat_id': update.message.chat_id,
    }

    logger.info(f"Preparing reminder '{thing_to_remind}' for {context['user_tag']}. Offering time options..")
    chat_data.update(context)

    # User time selection will be captured by reminder_callback
    _show_time_options(update, thing_to_remind)


def _show_time_options(update, to_remind):
    time_options = time_options_keyboard()
    if not to_remind:
        # User did not specify what to remind. (bare /remind with no args)
        text = REMINDER_DEFAULT
    else:
        text = f'Elegí cuando querés que te recuerde `{to_remind}` ⏱'

    update.effective_message.reply_text(
        text=text,
        reply_markup=time_options,
        parse_mode='markdown'
    )


def reminder_callback(bot, update, chat_data, job_queue):
    if not chat_data:
        update.callback_query.message.reply_text(MISSING_CHAT_DATA)
        return

    requested_delay = int(get_delay(update.callback_query.data))

    when, when_iso = _datetime_from_answer(requested_delay)
    chat_data.update({'remind_date': when_iso, 'requested_delay': requested_delay})
    job_context = copy.deepcopy(chat_data)

    logger.info("Setting up new reminder. %s", job_context)
    success = _add_reminder_job(bot, update, job_queue, job_context, when)
    if success:
        _reply_reminder_details(update, job_context)
    else:
        update.callback_query.message.edit_text(
            text=f"🚫 Error guardando el reminder. Intentá de nuevo más tarde",
            reply_markup=None
        )


def _add_reminder_job(bot, update, job_queue, job_context, when):
    logger.info(f"Adding job to db..")
    added = add_job_to_db(job_context)
    update.callback_query.answer(text='')
    if added:
        job_queue.run_once(send_notification, when, context=job_context)
        logger.info(f"Job added to job queue and db.")
    else:
        logger.error('Could not save reminder job')
        send_message_to_admin(bot, f"Error saving reminder.\n CONTEXT:\n{job_context}\n")

    return added


def _reply_reminder_details(update, job_context):
    bs_as_date = datetime.now(pytz.timezone(BUENOS_AIRES_TIMEZONE)) + timedelta(seconds=job_context['requested_delay'])
    update.callback_query.message.edit_text(
        text=(f"✅ Listo, te voy a recordar `{job_context['thing_to_remind']}`"
              f" el {bs_as_date.strftime('%d/%m')} a las {bs_as_date.strftime('%H:%M')} 🔔"),
        reply_markup=None,
        parse_mode='markdown'
    )
