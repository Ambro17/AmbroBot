import re

# Aliases for callback times
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

# Regex for redirecting callbacks and reading answers
REMIND = r'REMINDERS_'
REMINDERS_REGEX = re.compile(REMIND)
REMIND_TIME = REMIND + '{}'
GUESS_FROM_INPUT = REMIND + 'GUESS_FROM_INPUT'

TIME_ICONS = ['⏰', '🔊', '🔈', '🔉', '📣', '📢', '❕', '🎉', '🎊', '⏱']

GMT_BUENOS_AIRES = -3
