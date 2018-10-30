import logging

import os
import psycopg2
from telegram import MessageEntity

from utils.decorators import admin_only, log_time

logger = logging.getLogger(__name__)

DB = os.environ['DATABASE_URL']


def tag_all(bot, update):
    """Reply to a message containing '@all' tagging all users so they can read the msg."""
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute("select * from t3;")
                users = cursor.fetchone()
                update.message.reply_markdown(
                    text=users[0] if users else 'No users added to @all tag.',
                    quote=True,
                )
    except Exception as e:
        logger.exception("Error writing to db")
        logger.error(e)


@log_time
@admin_only
def set_all_members(bot, update, **kwargs):
    """Set members to be tagged when @all keyword is used."""
    msg = kwargs.get('args')
    if not msg:
        logger.info("No users passed to set_all_members function. kwargs: %s",
            kwargs,
        )
        return

    user_entities = update.message.parse_entities(
        [MessageEntity.MENTION, MessageEntity.TEXT_MENTION]
    )
    updated = update_all_users(user_entities)
    if updated:
        bot.send_message(
            chat_id=update.message.chat_id, text='Users added to the @all tag'
        )
    else:
        pass
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Algo pasó. Hablale a @BoedoCrow y pedile que vea los logs.',
        )


def update_all_users(users):
    """Tag users whether they have username or not.

    Users in telegram may or may not have username.
    If they have, tagging them is just writing @<username>.
    But if they don't one must use markdown syntax
    to tag them.

    This function transforms a text_mention
    or mention MessageEntity into a ready-to-be-tagged string,
    If they have a username, the value of users dict
    contains @<username> and that is sufficient to tag them.
    If they don't we must get their ids and tag them via
    markdown syntax [visible_name](tg://user?id=<user_id>)

    Args:
        users: dict of type MessageEntity: str

    Returns:
        tagged_users list(str): List of ready-to-be-tagged users.

    """
    # Get users mentions
    ready_to_be_tagged_users = []
    for entity, value in users.items():
        if entity['type'] == 'text_mention':
            ready_to_be_tagged_users.append(
                f"[@{entity.user.first_name}](tg://user?id={entity.user.id})"
            )
        elif entity['type'] == 'mention':
            ready_to_be_tagged_users.append(value)

    # Save it to db
    users = ' '.join(ready_to_be_tagged_users)
    logger.info("users %r", users)
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as curs:
                # Delete previous definition if any
                curs.execute("DELETE FROM t3;")
                # Add new values.
                curs.execute("INSERT INTO t3 (admins) VALUES (%s);", (users,))
                logger.info("Users '%s' successfully added to db", users)
                conn.commit()
                success = True
    except Exception:
        logger.exception("Error writing to db")
        success = False

    return success
