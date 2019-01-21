from datetime import timedelta

from telegram.ext import run_async, CommandHandler

from commands.meeting.db_operations import get_meetings, delete_meeting_db
from commands.remindme.constants import GMT_BUENOS_AIRES
from utils.decorators import group_only, log_time, send_typing_action


@log_time
@send_typing_action
@run_async
@group_only
def show_meetings(bot, update):
    meetings = get_meetings()
    if meetings:
        update.message.reply_text(
            '\n'.join(
                f"{meet.name} | {_localize_time(meet.datetime)}"
                for meet in meetings
            )
        )
    else:
        update.message.reply_text('📋 No hay ninguna meeting guardada todavía')


def _localize_time(date):
    # Turns UTC time into buenos aires time.
    date = date + timedelta(hours=GMT_BUENOS_AIRES)
    return date.strftime('%A %d/%m %H:%M').capitalize()


@log_time
@send_typing_action
@run_async
@group_only
def delete_meeting(bot, update, args):
    if not args:
        update.message.reply_text('Tenés que poner el nombre de la reunión a borrar')
        return

    name = ' '.join(args)
    deleted = delete_meeting_db(name)
    if deleted:
        update.message.reply_text(f'Reunión `{name}` borrada', parse_mode='markdown')
    else:
        update.message.reply_text('No existe reunión bajo ese nombre')


show_meetings_handler = CommandHandler('meetings', show_meetings)
delete_meeting_handler = CommandHandler('delmeeting', delete_meeting, pass_args=True)
