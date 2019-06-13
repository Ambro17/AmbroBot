from telegram.ext import run_async, CommandHandler

from commands.subte.suscribers.constants import MISSING_LINEA_MESSAGE, LINEAS, UNSUSCRIBED_MESSAGE
from commands.subte.suscribers.db import get_suscriptors, remove_subte_suscriber
from commands.subte.suscribers.utils import add_suscriber_to_linea
from updater import elbot
from utils.decorators import handle_empty_arg, private_chat_only, admin_only, send_typing_action


@send_typing_action
@run_async
@private_chat_only
@handle_empty_arg(required_params=('args',), error_message=MISSING_LINEA_MESSAGE, parse_mode='markdown')
@elbot.command(command='suscribe', pass_args=True)
def suscribe(bot, update, args):
    """Suscribe to a subte line to receive updates via private message."""
    linea = args[0]
    if linea.upper() not in LINEAS:
        update.message.reply_text(
            '🚫 La linea elegida no existe. Intentá de nuevo con `/suscribe <linea_id>`',
            parse_mode='markdown'
        )
        return

    linea = linea.upper()
    user = update.message.from_user
    added = add_suscriber_to_linea(user.id, user.name, linea)
    if added:
        msg = f'✅ Listo. Serás notificado via chat privado de los updates de la linea {linea}'
    else:
        msg = f'🚫 Algo salió mal. Mejor intentá más tarde'

    update.message.reply_text(msg)


@send_typing_action
@run_async
@handle_empty_arg(required_params=('args',), error_message=UNSUSCRIBED_MESSAGE, parse_mode='markdown')
@elbot.command(command='unsuscribe', pass_args=True)
def unsuscribe(bot, update, args):
    linea = args[0]
    if linea.upper() not in LINEAS:
        update.message.reply_text('🚫 La linea elegida no existe.')
        return

    user = update.message.from_user
    removed = remove_subte_suscriber(str(user.id), linea.upper())
    if removed:
        msg = f'✅ Listo. Tu suscripción quedó cancelada'
    else:
        msg = f'👻 Algo salió mal. Mejor intentá más tarde'

    update.message.reply_text(msg, quote=False)


@send_typing_action
@run_async
@admin_only
@elbot.command(command='suscribers')
def suscribers(bot, update):
    items = get_suscriptors()
    if items:
        update.message.reply_text(
            '\n'.join(
                f"{item.user_name} | {item.linea.upper()}"
                for item in items
            )
        )
    else:
        update.message.reply_text('📋 Aún no hay suscriptores a los subte updates')
