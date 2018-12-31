import logging

from commands.remindme.job import send_notification
from commands.remindme.persistence.db_ops import get_reminders
from commands.remindme.utils import isoformat_to_datetime

logger = logging.getLogger(__name__)


def load_reminders(bot, job_queue):
    """Query all non-expired reminders and add them to the job_queue if they are not present."""
    try:
        reminders = get_reminders(expired=False)
    except Exception:
        logger.error("Reminders could not be restored from db", exc_info=True)
        return 0

    recovered_jobs = 0
    job_names = [j.name for j in job_queue.jobs()]
    reminders_to_recover = [r for r in reminders if r.text not in job_names]

    logger.info(f'Found {len(reminders_to_recover)} reminders in db that are not in the job_queue')
    for reminder in reminders_to_recover:
        # Readd the reminder in the db.
        job_queue.run_once(
            send_notification,
            when=isoformat_to_datetime(reminder.remind_time),
            context=reminder.job_context,
            name=reminder.text
        )
        logger.info('Job readded to job queue from database. %s', reminder)
        recovered_jobs += 1

    return recovered_jobs
