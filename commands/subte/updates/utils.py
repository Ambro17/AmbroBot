import logging
import random
import re

from commands.subte.constants import DELAY_ICONS, SUBWAY_ICON, SUBWAY_LINE_OK
from commands.subte.suscribers.db import get_suscriptors_by_line


logger = logging.getLogger(__name__)

LINEA = re.compile(r'Linea([A-Z]{1})')


def get_update_info(alert):
    linea = _get_linea_name(alert)
    incident = _get_incident_text(alert)
    return linea, incident


def _get_linea_name(alert):
    try:
        nombre_linea = alert['informed_entity'][0]['route_id']
    except (IndexError, KeyError):
        return None

    try:
        nombre_linea = LINEA.match(nombre_linea).group(1)
    except AttributeError:
        # There was no linea match -> Premetro y linea Urquiza
        nombre_linea = nombre_linea.replace('PM-', 'PM ')

    return nombre_linea


def _get_incident_text(alert):
    translations = alert['header_text']['translation']
    spanish_desc = next((translation
                         for translation in translations
                         if translation['language'] == 'es'), None)
    if spanish_desc is None:
        logger.info('raro, no tiene desc en español. %s' % alert)
        return None

    return spanish_desc['text']


def prettify_updates(updates):
    delay_icon = random.choice(DELAY_ICONS)
    return '\n'.join(
        pretty_update(linea, status, delay_icon)
        for linea, status in updates.items()
    )


def pretty_update(linea, update, icon=SUBWAY_ICON):
    return f'{linea} | {icon}️ {update}'


def send_new_incident_updates(bot, context, status_updates):
    msg_count = 0
    new_incidents = {line: update for line, update in status_updates.items() if update != context.get(line)}
    logger.info('New incidents:\n%s', new_incidents)
    for linea, update in new_incidents.items():
        for suscription in get_suscriptors_by_line(linea):
            # Status Update may have changed but because another line is suspended.
            # If we are here, it means the status of the suscribed line has changed.
            logger.info(f'Sending update message on line {linea} to {suscription.user_name}')
            bot.send_message(chat_id=suscription.user_id, text=pretty_update(linea, update))
            msg_count += 1

    return msg_count


def send_service_normalization_updates(bot, context, status_updates):
    # Send update on lines that had issues but were solved
    # Solved issues were part of the context, but are not part of the status_updates, because they were solved.
    msg_count = 0
    solved_issues = {line: st for line, st in context.items() if line not in status_updates}
    logger.info('Solved issues:\n%s', solved_issues)
    for line, previous_status in solved_issues.items():
        for suscription in get_suscriptors_by_line(line):
            logger.info(f'Send OK status about {line} to {suscription.user_name}')
            bot.send_message(chat_id=suscription.user_id, text=SUBWAY_LINE_OK.format(line))
            msg_count += 1

    return msg_count
