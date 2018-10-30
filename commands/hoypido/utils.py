# Credits to @yromero

import logging
from datetime import datetime

import requests

from utils.command_utils import monospace

logger = logging.getLogger(__name__)

ONAPSIS_SALUDABLE = "https://api.hoypido.com/company/326/menus"
ONAPSIS_PAGO = "https://api.hoypido.com/company/327/menus"

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(0, 7)

day_names = {
    MONDAY: 'Lunes',
    TUESDAY: 'Martes',
    WEDNESDAY: 'Miércoles',
    THURSDAY: 'Jueves',
    FRIDAY: 'Viernes',
    SATURDAY: 'Sábado',
    SUNDAY: 'Domingo',
}


def get_comidas():
    menu_por_dia = {}
    response = requests.get(ONAPSIS_SALUDABLE, timeout=2)
    for day_offer in response.json():
        food_offers = sorted([food_offer["name"] for food_offer in day_offer['options']])
        date = datetime.strptime(day_offer["active_date"], "%Y-%m-%dT%H:%M:%S")
        menu_por_dia[date.weekday()] = food_offers

    return menu_por_dia


def prettify_food_offers(menu_por_dia, day=None):
    today = datetime.today().weekday()

    if day is None:
        day = MONDAY if today in (SATURDAY, SUNDAY) else today

    try:
        food_offers = menu_por_dia[day]
    except KeyError:
        # If you ask on tuesday at night, only wednesday food will be retrieved.
        logger.info("Menu for today not available. Showing tomorrow's menu. %s", menu_por_dia)
        day = day + 1
        food_offers = menu_por_dia[day]

    header = [f"\t\t\t\t\tMenú del {day_names[day]}"]
    return monospace('\n'.join(header + food_offers + ['⚡️ by Yona']))
