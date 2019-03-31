import datetime
import logging

import requests

from commands.feriados.constants import month_names, FERIADOS_URL, ESP_DAY

logger = logging.getLogger(__name__)


def get_feriados(year):
    try:
        url = FERIADOS_URL.format(year=year)
        r = requests.get(url, params={'incluir': 'opcional'})
        logger.info(f'Retrieved feriados from {r.url}')
    except Exception:
        logger.error("Error requestion feriados", exc_info=True)
        return None
    if r.status_code != 200:
        logger.info(f"Response not 200. {r.status_code} {r.reason}")
        return None

    feriados = r.json()
    logger.info("Feriados: %s", feriados)

    return feriados


def filter_past_feriados(today, feriados):
    """Returns the future feriados. Filtering past feriados."""
    return (
        f for f in feriados
        if (f['mes'], f['dia']) > (today.month, today.day)
    )


def next_feriado_message(today, nextest_feriado):
    """Get message corresponding to how many days are left until next feriado"""
    # Get days until next feriado
    next_feriado_date = datetime.datetime(day=nextest_feriado['dia'], month=nextest_feriado['mes'], year=today.year,
                                          hour=today.hour, minute=today.minute, second=min(today.second + 1, 59),
                                          tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))

    # In python, timedeltas can have negative days if we do a-b and b > a). See timedelta docs for details
    faltan = (next_feriado_date - today)
    days_to_feriado = max(faltan.days, 0)

    if days_to_feriado == 0:
        feriado_msg = f"Hoy es feriado por *{nextest_feriado['motivo']}*! 🎉\n"
    else:
        feriado_msg = (
            f"Faltan *{days_to_feriado} días* para el próximo feriado del"
            f" *{ESP_DAY[next_feriado_date.weekday()]}"
            f" {nextest_feriado['dia']} de {month_names[nextest_feriado['mes']]}*"
            f" por el _{nextest_feriado['motivo']}_\n"
        )

    return feriado_msg


def prettify_feriados(feriados, limit=None):
    """Receives a feriado generator of dict of following feriados and pretty prints them.
    ({
        "motivo": "Año Nuevo",
        "tipo": "inamovible",
        "dia": 1,
        "mes": 1,
        "id": "año-nuevo"
    }, {
        "motivo": "Carnaval",
        "tipo": "inamovible",
        "dia": 4,
        "mes": 3,
        "id": "carnaval"
    },
        ...
    )
    Output:
        👉 25 de diciembre  -  Navidad | inamovible
        👉 31 de diciembre  -  Feriado Puente Turístico | puente
    """
    res = ''
    for feriado in list(feriados)[:limit]:
        # Improvement. Print mes header before feriados of that month
        fecha = f"{feriado['dia']} de {month_names[feriado['mes']]}"
        res += f"👉 {fecha:<16} -  {feriado['motivo']} | _{feriado['tipo']}_\n"

    return res


def read_limit_from_args(args):
    """Limit the amount of feriados to show."""
    DEFAULT = 10

    if not args:
        return DEFAULT
    elif args[0].upper() == 'ALL':
        # my_list[:None] == my_list
        return None
    else:
        try:
            return int(args[0])
        except (TypeError, ValueError):
            return DEFAULT
