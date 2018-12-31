import logging
import random

from commands.remindme.constants import TIME_ICONS
from commands.remindme.persistence.db_ops import remove_reminder
from commands.remindme.utils import reminder_key

logger = logging.getLogger(__name__)


def send_notification(bot, job):
    random_time_emoji = random.choice(TIME_ICONS)
    to_remind = job.context['thing_to_remind'] or 'Reminder!'
    bot.send_message(
        chat_id=job.context['chat_id'],
        text=f"{job.context['user_tag']} {to_remind} {random_time_emoji} ",
        # reply_markup=remind_again_or_done()
    )
    logger.info(f"User {job.context['user_tag']} was reminded of {to_remind}")
    job.schedule_removal()
    remove_reminder(reminder_key(job.context))
