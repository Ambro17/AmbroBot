import logging
import random
from datetime import datetime, timedelta, timezone

from commands.remindme.constants import TIME_ICONS, GMT_BUENOS_AIRES

logger = logging.getLogger(__name__)


def reminder_callback(bot, update, chat_data, job_queue):
    job_context = {
        'chat_id': update.callback_query.message.chat_id,
        'text': chat_data['to_remind'],
        'user': chat_data['user']
    }
    delay_requested = int(update.callback_query.data)
    update.callback_query.answer(text='')

    # Set up the job
    logger.info("Setup new job. context: %s", job_context)
    job_queue.run_once(send_text, delay_requested,
                       context=job_context)  # Feature: manage added jobs in db to survive bot shutdown

    # Manage hours to show in Bs As local time.
    buenos_aires_offset = timezone(timedelta(hours=GMT_BUENOS_AIRES))
    remind_date = datetime.now(buenos_aires_offset) + timedelta(seconds=delay_requested)

    # Send reply with the hour of the reminder
    update.callback_query.message.edit_text(
        text=f"✅ Listo, te voy a recordar '{chat_data['to_remind']}' a las {remind_date.strftime('%H:%M')} 🔔",
        reply_markup=None
    )


def send_text(bot, job):
    random_time_emoji = random.choice(TIME_ICONS)
    bot.send_message(
        chat_id=job.context['chat_id'],
        text=f"{job.context['user']} {random_time_emoji} {job.context['text']}"
    )
