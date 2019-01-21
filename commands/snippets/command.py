# -*- coding: UTF-8 -*-
from telegram.ext import run_async, RegexHandler, CommandHandler

from commands.snippets.constants import SAVE_REGEX, GET_REGEX, DELETE_REGEX
from commands.snippets.utils import (
    lookup_content,
    save_to_db,
    select_all_snippets,
    remove_snippet,
    link_key)
from utils.decorators import send_typing_action, log_time, admin_only, requires_auth


@log_time
@send_typing_action
@run_async
@requires_auth
def save_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = kwargs['groupdict'].get('content')

    if None in (key, content):
        message = 'No respetaste el formato. Intentá de nuevo'
    else:
        sucess, error_message = save_to_db(key, content)
        if sucess:
            message = f'Info guardada ✅.\nPodés leerla escribiendo `@get {key}`'
        else:
            message = error_message.format(key)

    bot.send_message(
        chat_id=update.message.chat_id, text=message, parse_mode='markdown'
    )


@log_time
@send_typing_action
@run_async
@requires_auth
def get_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = lookup_content(key)
    if content:
        key, saved_data = content
        bot.send_message(chat_id=update.message.chat_id, text=saved_data)
    else:
        message = f"No hay nada guardado bajo '{key}'.\nProbá /snippets para ver qué datos están guardados"
        bot.send_message(chat_id=update.message.chat_id, text=message)


@log_time
@send_typing_action
@run_async
@requires_auth
def get_snippet_command(bot, update, args):
    """Duplicate of get_snippet because only /commands can be clickable."""
    if not args:
        update.message.reply_text('Faltó poner la clave `/get <clave>`', parse_mode='markdown')
        return
    key = ' '.join(args)
    content = lookup_content(key)
    if content:
        key, saved_data = content
        bot.send_message(chat_id=update.message.chat_id, text=saved_data)
    else:
        message = f"No hay nada guardado bajo '{key}'.\nProbá /snippets para ver qué datos están guardados"
        bot.send_message(chat_id=update.message.chat_id, text=message)


@log_time
@send_typing_action
@run_async
@requires_auth
def show_snippets(bot, update):
    answers = select_all_snippets()
    if answers:
        keys = [f'🔑  {link_key(key)}' for id, key, content in answers]
        reminder = ['Para ver algún snippet » `/get <clave>` o\nclickeá la clave y reenviá a un chat donde esté yo']
        update.message.reply_text(text='\n\n'.join(keys + reminder), parse_mode='markdown')
    else:
        update.message.reply_text(
            'No hay ningún snippet guardado!\nPodés empezar usando `#key snippet_to_save`',
            parse_mode='markdown',
        )


@run_async
@log_time
@admin_only
def delete_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    if not key:
        update.message.reply_text('Te faltó poner qué snippet borrar')
        return

    removed = remove_snippet(key)
    if removed:
        message = f"✅ El snippet `{key}` fue borrado"
    else:
        message = 'No se pudo borrar la pregunta.'

    update.message.reply_text(message, parse_mode='markdown')


save_snippet_handler = RegexHandler(SAVE_REGEX, save_snippet, pass_groupdict=True)
get_snippet_handler = RegexHandler(GET_REGEX, get_snippet, pass_groupdict=True)
delete_snippet_handler = RegexHandler(DELETE_REGEX, delete_snippet, pass_groupdict=True)
snippet_get_command = CommandHandler('get', get_snippet_command, pass_args=True)
show_snippets_handler = CommandHandler('snippets', show_snippets)
