# Credits to @yromero

from datetime import datetime
import requests

from utils.command_utils import monospace

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

    food_offers = menu_por_dia[day]
    food_offers.insert(0, f"\t\t\tMenú del {day_names[day]}")
    return monospace('\n'.join(food_offers))
