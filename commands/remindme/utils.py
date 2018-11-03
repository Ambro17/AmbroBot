from commands.remindme.constants import REMIND_TIME


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
        raise ValueError("Delay string has a wrong format. "
                         "Expected: REMINDERS_<int> but"
                         "Received: %s", delay_string)