import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

LINEA = re.compile(r'Alert_Linea([A-Z]{1})')


def check_update():
    params = {
        'client_id': os.environ['CABA_CLI_ID'],
        'client_secret': os.environ['CABA_SECRET'],
        'json': 1,
    }
    url = 'https://apitransporte.buenosaires.gob.ar/subtes/serviceAlerts'
    r = requests.get(url, params=params)

    if r.status_code != 200:
        logger.info('Response failed. %s %s' % (r.status_code, r.reason))
        return None

    data = r.json()

    alerts = data['entity']
    updates = []
    logger.info('Alerts: %s', alerts)
    for alert in alerts:
        alert_id = alert['id']
        nombre_linea = LINEA.match(alert_id).group(1) if LINEA.match(alert_id) else alert_id
        info = alert['alert']
        translations = info['header_text']['translation']
        spanish_desc = next((translation
                             for translation in translations
                             if translation['language'] == 'es'), None)
        if not spanish_desc:
            logger.info('raro, no tiene desc en espanol. %s' % alert)
            continue

        text = spanish_desc['text']
        updates.append((nombre_linea, text))

    return updates


def prettify_updates(updates):
    return '\n'.join(f'{linea} | ⚠️ {status}' for linea, status in updates)


def subte_updates_cron(bot, job):
    try:
        status_updates = check_update()
    except Exception:
        logger.exception('An unexpected error ocurred when fetching updates.')
        return
    context = job.context
    if status_updates is not None and status_updates != context.get('last_update'):
        logger.info('Updating subte status')
        pretty_update = prettify_updates(status_updates)
        bot.send_message(chat_id='@subtescaba', text=pretty_update)
        context['last_update'] = status_updates
    else:
        logger.info(
            "Subte status has not changed. Avoid posting new reply. %s", status_updates
        )
