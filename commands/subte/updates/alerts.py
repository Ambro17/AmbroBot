import logging
import os
import random
import re

import requests

from commands.subte.constants import DELAY_ICONS, SUBWAY_STATUS_OK, SUBWAY_ICON, SUBWAY_LINE_OK
from commands.subte.suscribers.db import get_suscriptors_by_line

logger = logging.getLogger(__name__)

LINEA = re.compile(r'Linea([A-Z]{1})')


def subte_updates_cron(bot, job):
    try:
        status_updates = check_update()
    except Exception:
        logger.exception('An unexpected error ocurred when fetching updates.')
        return
    context = job.context
    if status_updates is not None and status_updates != context.get('last_update'):
        logger.info('Updating subte status')
        if not status_updates:
            # There are no incidents to report.
            pretty_update = SUBWAY_STATUS_OK
        else:
            pretty_update = prettify_updates(status_updates)

        bot.send_message(chat_id='@subtescaba', text=pretty_update)
        update_context_per_line(status_updates, context)
        try:
            notify_suscribers(bot, status_updates, context)
        except Exception:
            logger.error("Could not notify suscribers", exc_info=True)
        context['last_update'] = status_updates
    else:
        logger.info(
            "Subte status has not changed. Avoid posting new reply. %s", status_updates
        )


def check_update():
    """Returns status incidents per line.

    None if response code is not 200
    empty dict if there are no updates
    dict with linea as keys and incident details as values.

    Returns:
        dict|None: mapping of line incidents
    """
    params = {
        'client_id': os.environ['CABA_CLI_ID'],
        'client_secret': os.environ['CABA_SECRET'],
        'json': 1,
    }
    url = 'https://apitransporte.buenosaires.gob.ar/subtes/serviceAlerts'
    r = requests.get(url, params=params)

    if r.status_code != 200:
        logger.info('Response failed. %s, %s' % (r.status_code, r.reason))
        return None

    data = r.json()

    alerts = data['entity']
    logger.info('Alerts: %s', alerts)

    return dict(_get_update_info(alert['alert']) for alert in alerts)


def _get_update_info(alert):
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


def notify_suscribers(bot, status_updates, context):
    """Notify suscribers of updates on their lines.

    Args:
        bot: telegram.bot instance
        status_updates (dict): New incidents reported by the api
        context (dict): Incidents last time we checked
    """
    # Send updates of new incidents
    for linea, update in status_updates.items():
        for suscription in get_suscriptors_by_line(linea):
            if update != context.get(linea):
                # Status Update may have changed but because another line is suspended.
                # If we are here, it means the status of the suscribed line has changed.
                bot.send_message(chat_id=suscription.user_id, text=pretty_update(linea, update))
            else:
                logger.info(f'{linea} status has not changed')

    # Send update on lines that had issues but were solved
    for line, previous_status in context.items():
        if line not in status_updates:
            # If the line is not included anymore on status updates,
            # it means its now working normally.
            for suscription in get_suscriptors_by_line(line):
                bot.send_message(chat_id=suscription.user_id, text=SUBWAY_LINE_OK.format(line))


def update_context_per_line(status_updates, context):
    if not status_updates:
        # All lines work normally. Remove all entries from context.
        context.clear()
    else:
        context.update(
            {linea: status for linea, status in status_updates}
        )


def prettify_updates(updates):
    delay_icon = random.choice(DELAY_ICONS)
    return '\n'.join(
        pretty_update(linea, status, delay_icon)
        for linea, status in updates.items()
    )


def pretty_update(linea, update, icon=SUBWAY_ICON):
    return f'{linea} | {icon}️ {update}'

