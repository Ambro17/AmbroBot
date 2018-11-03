import re

# Aliases for callback times
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

# Regex for redirecting callbacks and reading answers
REMIND_BASE = r'REMINDERS_'
REMINDERS = f'{REMIND_BASE}|\d+'  # If it starts with reminders prefix or callback_data is a number
REMINDERS_REGEX = re.compile(REMINDERS)

GUESS_FROM_INPUT = REMIND_BASE + 'GUESS_FROM_INPUT'

TIME_ICONS = ['⏰', '🔊', '🔈', '🔉', '📣', '📢', '❕', '🎉', '🎊', '⏱']
