import datetime
import logging

import requests

from commands.feriados.constants import month_names, FERIADOS_URL

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


def filter_feriados(today, feriados):
    """Returns the future feriados. Filtering past feriados."""
    return [
        f for f in feriados
        if (f['mes'] == today.month and f['dia'] >= today.day)
           or f['mes'] > today.month
    ]


def next_feriado_message(today, feriados):
    """Get message corresponding to how many days are left until next feriado"""
    # Get days until next feriado
    nextest_feriado = feriados[0]
    next_feriado_date = datetime.datetime(day=nextest_feriado['dia'], month=nextest_feriado['mes'], year=today.year,
                                          tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))

    # In python, timedeltas can have negative days if we do a-b and b > a). See timedelta docs for details
    faltan = (next_feriado_date - today)
    days_to_feriado = max(faltan.days, 0)

    if days_to_feriado == 0:
        feriado_msg = f"Hoy es feriado por *{nextest_feriado['motivo']}*! 🎉\n"
    else:
        feriado_msg = (
            f"Faltan *{days_to_feriado} días* para el próximo feriado del"
            f" *{nextest_feriado['dia']} de {month_names[nextest_feriado['mes']]}*\n"
        )

    return feriado_msg


def prettify_feriados(feriados):
    """Receives a feriado dict of following feriados and pretty prints them.
    [{
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
    ]
    Output:
        👉 25 de diciembre  -  Navidad | inamovible
        👉 31 de diciembre  -  Feriado Puente Turístico | puente
    """
    res = ''
    for feriado in feriados:
        # Improvement. Print mes header before feriados of that month
        fecha = f"{feriado['dia']} de {month_names[feriado['mes']]}"
        res += f"👉 {fecha:<16} -  {feriado['motivo']} | _{feriado['tipo']}_\n"

    return res
