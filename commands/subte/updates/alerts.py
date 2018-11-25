import logging
import os
import random
import re

import requests

from commands.subte.constants import DELAY_ICONS

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
            pretty_update = '✅ Todos los subtes funcionan con normalidad'
        else:
            pretty_update = prettify_updates(status_updates)

        bot.send_message(chat_id='@subtescaba', text=pretty_update)
        context['last_update'] = status_updates
    else:
        logger.info(
            "Subte status has not changed. Avoid posting new reply. %s", status_updates
        )


def check_update():
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

    return [_get_update_info(alert['alert']) for alert in alerts]


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
        nombre_linea = nombre_linea.replace('PM-', 'Premetro ')

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
        f'{linea} | {delay_icon}️ {status}'
        for linea, status in updates
    )
