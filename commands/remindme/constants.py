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

NOTIFICATION = r'NOTIFICATION_'
DONE = NOTIFICATION + 'DONE'
REMIND_AGAIN = NOTIFICATION + 'REMIND_AGAIN'

TIME_ICONS = ['⏰', '🔊', '🔈', '🔉', '📣', '📢', '❕', '🎉', '🎊', '⏱']
DONE_ICONS = '🏅🎖🥇🏆👏👌👍🙌'

GMT_BUENOS_AIRES = -3
BUENOS_AIRES_TIMEZONE = 'America/Argentina/Buenos_Aires'

REMINDER_DEFAULT = ('Elegí cuando querés que te recuerde que tenías que hacer algo\n'
                    '`💬 Tip: La próxima me podés decir qué querías recordar con /remind <algo>`')

MISSING_CHAT_DATA = 'I forgot what i had to remind you!'
