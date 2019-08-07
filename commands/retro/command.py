import logging
from datetime import datetime as d, timezone, timedelta

from telegram.ext import run_async

from commands.retro.models import RetroItem, Session
from updater import elbot
from utils.constants import GMT_BUENOS_AIRES
from utils.decorators import send_typing_action, log_time, group_only, admin_only

logger = logging.getLogger(__name__)


@elbot.command(command='retro', pass_args=True)
@log_time
@send_typing_action
@run_async
@group_only
def retro_add(bot, update, args):
    if not args:
        update.message.reply_text(
            'Tenes que agregar algo al retro bucket. `/retro mas recursos`',
            parse_mode='markdown',
        )
        return
    retro_item = ' '.join(args)
    user = update.effective_user.first_name
    buenos_aires_offset = timezone(timedelta(hours=GMT_BUENOS_AIRES))
    date = d.now(buenos_aires_offset)
    save_retro_item(retro_item, user, date)
    update.message.reply_text(
        '✅ Listo. Tu mensaje fue guardado para la retro.\n'
        'Para recordarlo en la retro escribí `/retroitems`',
        parse_mode='markdown',
    )
    logger.info("Retro event added: %s %s %s", user, retro_item, date)


@log_time
def save_retro_item(retro_item, user, date_time):
    session = Session()
    item = RetroItem(user=user, text=retro_item, datetime=date_time)
    session.add(item)
    session.commit()


@elbot.command(command='retroitems')
@log_time
@send_typing_action
@run_async
@group_only
def show_retro_items(bot, update):
    items = get_retro_items()
    if items:
        update.message.reply_text(
            '\n\n'.join(
                f"*{item.user}* | {item.text.capitalize()} | {_localize_time(item.datetime)}"
                for item in items
            ),
            parse_mode='markdown'
        )
    else:
        update.message.reply_text('📋 No hay ningún retroitem guardado todavía')


@log_time
def get_retro_items():
    session = Session()
    return session.query(RetroItem).filter_by(expired=False).all()


def _localize_time(date):
    # Turns UTC time into buenos aires time.
    date = date + timedelta(hours=GMT_BUENOS_AIRES)
    return date.strftime('%A %d/%m %H:%M').capitalize()


@elbot.command(command='endretro')
@log_time
@admin_only
def expire_retro(bot, update):
    session = Session()
    for item in session.query(RetroItem):
        item.expired = True
    session.commit()
    update.message.reply_text('✅ Listo. El registro de retroitems fue reseteado.')
