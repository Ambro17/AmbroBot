from datetime import timedelta

MEETING_FILTER = r'MEETING_'
DAY_T = MEETING_FILTER + '{}'
MEETING_PERIOD = MEETING_FILTER + 'PERIOD_{}'
CANCEL = MEETING_FILTER + 'CANCEL'

time_delta_map = {
    'Weekly': timedelta(weeks=1),
    'Biweekly': timedelta(weeks=2),
    'Monthly': timedelta(weeks=4),
}
