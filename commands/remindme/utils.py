from datetime import timedelta, datetime
import logging

import dateparser

from commands.remindme.constants import REMIND_TIME
from commands.remindme.persistence.db_ops import add_reminder
from commands.remindme.persistence.models import Reminder
from utils.decorators import log_time

logger = logging.getLogger(__name__)


def remind_time(time):
    """Transforms seconds into a string to be matched with cback query handler

    3600 -> 'REMINDERS_3600'
    """
    return REMIND_TIME.format(time)


def get_delay(delay_string):
    """Do the inverse operation than _remind_time"""
    try:
        return delay_string.split('_')[1]
    except IndexError:
        raise ValueError(
            "Delay string has a wrong format. "
            "Expected: REMINDERS_<int> but"
            "Received: %s",
            delay_string,
        )


def _tag_user(user):
    if user.username:
        return f'@{user.username}'
    else:
        return f"[@{user.first_name}](tg://user?id={user.id})"


def _datetime_from_answer(time_delay):
    """Returns a datetime object and its isoformat from time_delay in seconds"""
    when = datetime.now() + timedelta(seconds=time_delay)
    return when, when.isoformat()


@log_time
def add_job_to_db(job_context: dict) -> bool:
    """Saves a reminder in db based on the job_context"""
    try:
        reminder = Reminder(
            text=job_context['thing_to_remind'],
            user_id=job_context['user_id'],
            user_tag=job_context['user_tag'],
            remind_time=job_context['remind_date'],
            chat_id=job_context['chat_id'],
            job_context=job_context,
            key=reminder_key(job_context)
        )
        add_reminder(reminder)
        return True
    except KeyError:
        logger.exception('Job context keys not properly initialized.')
        return False
    except Exception:
        logger.exception("Error saving reminder to db.")
        return False


def isoformat_to_datetime(date_string):
    return dateparser.parse(date_string)


def reminder_key(jc):
    return '>'.join((str(jc['user_id']), jc['thing_to_remind'], jc['remind_date']))
