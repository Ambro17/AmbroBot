import logging

from commands.remindme.persistence.models import Reminder, Session

logger = logging.getLogger(__name__)


def add_reminder(reminder):
    session = Session()
    session.add(reminder)
    session.commit()


def remove_reminder(key):
    session = Session()
    reminder = session.query(Reminder).filter_by(key=key).first()
    if reminder is None:
        logger.info("Reminder (%s) does not exist on db", key)
        deleted = False
    else:
        session.delete(reminder)
        session.commit()
        logger.info("Reminder (%s) DELETED", key)
        deleted = True

    return deleted


def get_reminders(**kwargs):
    session = Session()
    return session.query(Reminder).filter_by(**kwargs)
