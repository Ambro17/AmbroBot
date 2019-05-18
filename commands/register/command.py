import logging

from sqlalchemy.exc import IntegrityError
from telegram.error import BadRequest
from telegram.ext import CommandHandler

from commands.register.db import add_user, _get_users
from updater import elbot
from utils.decorators import handle_empty_arg, send_typing_action, admin_only
from utils.utils import send_message_to_admin


logger = logging.getLogger(__name__)


@elbot.route(command='register')
def register(bot, update):
    """A user that wants to access private commands must first register"""
    user = update.message.from_user
    user_data_string = _user_to_string(user)
    send_message_to_admin(
        bot,
        f'{user.name} wants to start using AmbroBot\n\n'
        f'User details:\n{user_data_string}',
    )
    update.message.reply_text('✅ Your registration request has been sent.\nPlease wait for approval.. ⏳', quote=False)


@handle_empty_arg(required_params=('args',))
@send_typing_action
@admin_only
@elbot.route(command='authorize', pass_args=True)
def authorize(bot, update, args):
    if not args:
        update.message.reply_text('Y el user?')
        return
    user = _string_to_user(args[0])
    added = add_user_to_db(user)
    if added:
        update.message.reply_text('✅ User added to db')
        # send message to new registered user
        try:
            bot.send_message(chat_id=user['id'], text='✅ Has sido autorizad@ para hablar con Cuervot!')
        except BadRequest:
            logger.error("Unable to send message. User hasn't talked yet privately with Cuervot.")
    else:
        update.message.reply_text('🚫 Error saving user to db')


@send_typing_action
@admin_only
@elbot.route(command='users')
def show_users(bot, update):
    users = _get_users()
    total_users = len(users)
    result = '\n'.join([str(user) for user in users])
    message = f'Total users: {total_users}\n{result}'
    update.message.reply_text(message)


def _user_to_string(user):
    """Receives a user object and returns a string representation"""
    return (
        f"id:{user.id};"
        f"first_name:{user.first_name};"
        f"last_name:{user.last_name};"
        f"username:{user.username}"
    )


def _string_to_user(user_string):
    """Receives a user string and returns a dict with its attributes."""
    try:
        fields = user_string.split(';')
        user_attrs = [f.split(':') for f in fields]
        user_dict = {
            attrib: value for attrib, value in user_attrs
        }
        return user_dict
    except ValueError:
        logger.info("Malformed user string")
        return None


def add_user_to_db(user):
    try:
        add_user(user)
        return True

    except IntegrityError:
        logger.error("User already exists")
        return False
    except Exception:
        logger.exception("Error saving user to db")
        return False


register_user = CommandHandler('register', register)
authorize_handler = CommandHandler('authorize', authorize, pass_args=True)
show_users_handler = CommandHandler('users', show_users)
