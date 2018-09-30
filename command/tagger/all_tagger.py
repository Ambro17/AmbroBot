import logging
import json

from telegram import MessageEntity

logger = logging.getLogger(__name__)

def tag_all(bot, update):
    """Reply to a message containing '@all' tagging all users so they can read the msg."""
    try:
       with open('all_users.json', 'r') as f:
           users = json.load(f)
           update.message.reply_markdown(
               text=' '.join(users['data']) if users else 'No users added to @all tag.',
               quote=True
           )
    except FileNotFoundError:
        logger.info("all_users file not found. Probably called before setting members")

def set_all_members(bot, update, **kwargs):
    """Set members to be tagged when @all keyword is used."""
    msg = kwargs.get('args')
    if not msg:
        logger.info("No users passed to set_all_members function."
                    " Arguments received %s", kwargs)
        return

    user_entities = update.message.parse_entities(
        [MessageEntity.MENTION, MessageEntity.TEXT_MENTION]
    )
    tagged_users = _tag_users(user_entities)
    with open("all_users.json", 'w') as f:
        f.write(json.dumps({'data': tagged_users}))
        logger.info("Users under @all tag updated. Members: %s", tagged_users)
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Users added to the @all tag'
        )

def _tag_users(users):
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
    ready_to_be_tagged_users = []
    for entity, value in users.items():
        if entity['type'] == 'text_mention':
            ready_to_be_tagged_users.append(
                f"[@{entity.user.first_name}](tg://user?id={entity.user.id})"
            )
        else:
            ready_to_be_tagged_users.append(value)

    return ready_to_be_tagged_users
