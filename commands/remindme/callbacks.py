import logging
import random
from datetime import datetime, timedelta, timezone

from commands.remindme.constants import TIME_ICONS, GMT_BUENOS_AIRES, DONE, DONE_ICONS, REMIND_AGAIN
from commands.remindme.keyboards import remind_again_or_done, time_options_keyboard
from commands.remindme.utils import get_delay

logger = logging.getLogger(__name__)


def reminder_callback(bot, update, chat_data, job_queue):
    job_context = {
        'chat_id': update.callback_query.message.chat_id,
        'text': chat_data['to_remind'],
        'user': chat_data['user'],
    }
    answer = update.callback_query.data

    update.callback_query.answer(text='')

    if answer == DONE:
        icon = random.choice(DONE_ICONS)
        update.callback_query.message.edit_text(f'Reminder resuelto {icon}')
        return
    elif answer == REMIND_AGAIN:
        update.callback_query.message.edit_text(
            text="Cuando querés que te notifique de nuevo? ⏳",
            reply_markup=time_options_keyboard(),
        )
        return
    else:
        requested_delay = int(get_delay(answer))

    # Set up the job
    logger.info("Setup new job. Context: %s, Chat Data: %s", job_context, chat_data)
    job_queue.run_once(
        send_notification, requested_delay, context=job_context
    )  # Feature: manage added jobs in db to survive bot shutdown

    # Manage hours to show in Bs As local time.
    buenos_aires_offset = timezone(timedelta(hours=GMT_BUENOS_AIRES))
    remind_date = datetime.now(buenos_aires_offset) + timedelta(seconds=requested_delay)

    # Send reply with the hour of the reminder
    update.callback_query.message.edit_text(
        text=f"✅ Listo, te voy a recordar `{chat_data['to_remind']}` a las {remind_date.strftime('%H:%M')} 🔔",
        reply_markup=None,
        parse_mode='markdown'
    )


def send_notification(bot, job):
    random_time_emoji = random.choice(TIME_ICONS)
    bot.send_message(
        chat_id=job.context['chat_id'],
        text=f"{job.context['user']} {random_time_emoji} {job.context['text']}",
        reply_markup=remind_again_or_done()
    )
