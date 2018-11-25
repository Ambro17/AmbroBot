import re

# Aliases for callback times
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

# Regex for redirecting callbacks and reading answers
REMIND = r'REMINDERS_'
REMINDERS_REGEX = re.compile(REMIND)
REMIND_TIME = REMIND + '{}'
DONE = REMIND + 'DONE'
REMIND_AGAIN = REMIND + 'REMIND_AGAIN'
GUESS_FROM_INPUT = REMIND + 'GUESS_FROM_INPUT'

TIME_ICONS = ['⏰', '🔊', '🔈', '🔉', '📣', '📢', '❕', '🎉', '🎊', '⏱']
DONE_ICONS = '🏅🎖🥇🏆👏👌👍🙌'

GMT_BUENOS_AIRES = -3

MISSING_ARG_MESSAGE = 'Me tenés que dar algo que recordar! `/remind comprar frutas`'
