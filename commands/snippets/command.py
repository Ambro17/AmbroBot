from telegram.ext import run_async

from commands.snippets.utils import lookup_content, save_to_db, select_all, remove_snippet
from decorators import send_typing_action, log_time, admin_only


@send_typing_action
@run_async
@log_time
def save_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = kwargs['groupdict'].get('content')

    if None in (key, content):
        message = 'No respetaste el formato. Intentá de nuevo'
    elif save_to_db(key, content):
        message = f'Info guardada ✅.\nPodés leerla escribiendo `@get {key}`'
    else:
        message = ('Algo salió mal y no pude guardar tu pregunta.\n'
                   'Podés intentar más tarde o aceptar que en el mundo reina el caos.')

    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode='markdown')


@send_typing_action
@run_async
@log_time
def get_snippet(bot, update, **kwargs):
    key = kwargs['groupdict'].get('key')
    content = lookup_content(key)
    if content:
        key, saved_data = content
        bot.send_message(chat_id=update.message.chat_id, text=saved_data)
    else:
        message = f"No hay nada guardado bajo '{key}'.\nProbá @saved_data para ver qué datos están guardados"
        bot.send_message(chat_id=update.message.chat_id, text=message)


@run_async
@log_time
@send_typing_action
def show_snippets(bot, update):
    answers = select_all()
    if answers:
        keys = [f'🔑  {key}' for id, key, content in answers]
        reminder = ['Para ver algunos de los snippet de arriba » `@get <snippet_key>`']
        update.message.reply_text(text='\n\n'.join(keys + reminder), parse_mode='markdown')
    else:
        update.message.reply_text('No hay ningún snippet guardado!\nPodés empezar usando `#key snippet_to_save`',
                                  parse_mode='markdown')


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
