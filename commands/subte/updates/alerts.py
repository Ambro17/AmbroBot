import logging
import os

import requests

from commands.subte.constants import SUBWAY_STATUS_OK
from commands.subte.updates.utils import (
    get_update_info,
    send_new_incident_updates,
    send_service_normalization_updates,
    prettify_updates,
)
from utils.utils import send_message_to_admin

logger = logging.getLogger(__name__)


def subte_updates_cron(bot, job):
    try:
        status_updates = check_update()
    except Exception:
        logger.exception('An unexpected error ocurred when fetching updates.')
        send_message_to_admin(bot, 'An unexpected error ocurred when requesting subte updates. Please see the logs.')
        return
    if status_updates is None:
        logger.error("The api did not respond with status ok.")
        send_message_to_admin(bot, 'Metrovias api is not operational. Check it please')
        return

    context = job.context
    logger.info('Checking if subte status has changed..\nSTATUS_UPDATE: %s\nCONTEXT: %s', status_updates, context)
    if status_updates != context:
        logger.info('Updating subte status...')
        if not status_updates:
            # There are no incidents to report.
            pretty_update = SUBWAY_STATUS_OK
        else:
            pretty_update = prettify_updates(status_updates)

        bot.send_message(chat_id='@subtescaba', text=pretty_update)
        logger.info('Update message sent to channel')
        try:
            notify_suscribers(bot, status_updates, context)
            logger.info('Suscribers notified of line changes')
        except Exception:
            logger.error("Could not notify suscribers", exc_info=True)

        # Now the context must reflect the new status_updates. Update context with new incidents.
        job.context = status_updates
        logger.info('Context updated with new status updates')

    else:
        logger.info("Subte status has not changed. Not posting new reply.")


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

    return dict(get_update_info(alert['alert']) for alert in alerts)


def notify_suscribers(bot, status_updates, context):
    """Notify suscribers of updates on their lines.
    We notify suscribers of new incidents and
    we notify suscribers when a line has no more incidents. That means its working normally

    Args:
        bot: telegram.bot instance
        status_updates (dict): New incidents reported by the api
        context (dict): Incidents last time we checked
    """
    # Send updates of new incidents
    sent_updates = send_new_incident_updates(bot, context, status_updates)
    logger.info(f'New incidents messages sent: {sent_updates}')

    sent_normalization_msgs = send_service_normalization_updates(bot, context, status_updates)
    logger.info(f'Service normalization messages sent: {sent_normalization_msgs}')
