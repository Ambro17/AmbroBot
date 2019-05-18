from datetime import datetime, timezone, timedelta
import logging

from telegram.ext import CommandHandler

from commands.feriados.utils import (
    get_feriados,
    prettify_feriados,
    filter_past_feriados,
    next_feriado_message,
    read_limit_from_args,
)
from updater import elbot

logger = logging.getLogger(__name__)


@elbot.route(command='feriados', pass_args=True)
def feriadosarg(bot, update, args):
    limit = read_limit_from_args(args)
    today = datetime.now(tz=timezone(timedelta(hours=-3)))
    following_feriados = _get_next_feriados(today)
    if following_feriados:
        header_msg = next_feriado_message(today, next(following_feriados))
        all_feriados = prettify_feriados(following_feriados, limit=limit)
        msg = '\n'.join([header_msg, all_feriados])
    else:
        msg = 'No hay más feriados este año'

    update.message.reply_text(msg, parse_mode='markdown')


@elbot.route(command='feriado')
def next_feriado(bot, update):
    today = datetime.now(tz=timezone(timedelta(hours=-3)))
    following_feriados = _get_next_feriados(today)
    if following_feriados:
        msg = next_feriado_message(today, next(following_feriados))
    else:
        msg = 'No hay más feriados este año'

    update.message.reply_text(msg, parse_mode='markdown')


def _get_next_feriados(today):
    feriados = get_feriados(today.year)
    if not feriados:
        return []

    return filter_past_feriados(today, feriados)
