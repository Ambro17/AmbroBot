from commands.meeting.models import Session, Meeting
from utils.decorators import log_time


@log_time
def save_meeting(name, date):
    session = Session()
    session.add(Meeting(name=name, datetime=date))
    session.commit()


@log_time
def get_meetings():
    return Session().query(Meeting).filter_by(expired=False).all()


@log_time
def delete_meeting_db(name):
    session = Session()
    meeting = session.query(Meeting).filter_by(name=name).first()
    if meeting is not None:
        session.delete(meeting)
        session.commit()
        return True

    return False
