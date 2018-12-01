import logging
from commands.feriados.constants import month_num, month_names, DAYS_REGEX

logger = logging.getLogger(__name__)

def get_feriados(soup):
    feriados = {}
    meses = soup.find_all('div', class_='mes')
    logger.info("Meses: %s", meses)

    for mes in meses:
        mes_num = month_num[get_name(mes)]
        feriados[mes_num] = feriados_del_mes(mes)

    return feriados


def get_name(mes):
    return mes.h2.text.lower()


def feriados_del_mes(mes):
    """
    <div class="fer">
        <p>24. Día Nacional de la Memoria por la Verdad y la Justicia.
            <span class="sr-only">Feriado inamovible</span>
        </p>
        <p>29. Jueves Santo.
            <span class="sr-only">Día no laborable</span>
        </p>
        <p>30. Viernes Santo.
            <span class="sr-only">Feriado inamovible</span>
        </p>
        <p>30 y 31. Pascuas Judías.
            <span class="sr-only">Día no laborable</span>
        </p>
    </div>
    Args:
        mes: bs4 tag with name of the month and a subling with feriados descriptions

    Returns:
        dict
    """
    feriados = {}
    fer_div = mes.parent.find('div', class_='fer')
    for fer_desc in fer_div.find_all('p'):
        tipo_de_feriado = fer_desc.span.extract()  # No laborable, inamovible o trasladable
        feriados.update(
            feriados_from_string(fer_desc.text.strip(), tipo_de_feriado.text.strip())
        )
    return feriados


def feriados_from_string(date, tipo_feriado):
    """Returns feriados by day, with description.

    Args:
        date: string with day and feriado description

    Returns:
        dict: feriado days as key and description as value

    example input:
        '1, 5 y 6. Pascuas Judías.', 'Día no laborable'
    example output:
        {
            1: 'Pascuas Judías.', 'Día no laborable'),
            2: 'Pascuas Judías.', 'Día no laborable')
            3: 'Pascuas Judías.', 'Día no laborable')
        }
    """
    dates, description = date.split('.', 1)
    days = [int(d) for d in DAYS_REGEX.findall(dates)]

    return {day: (description.strip(), tipo_feriado) for day in days}


def prettify_feriados(feriados, from_month=None):
    """Receives a feriado dict and pretty prints the future feriados."""
    if from_month:
        feriados = {k: v for k, v in feriados.items() if k >= from_month}
    res = ''
    for month_num, days in feriados.items():
        month_name = month_names[month_num]
        all_days = '\n'.join(f"{dia}. {evento[0]}" for dia, evento in days.items())
        res += f"{month_name.capitalize()}\n{all_days}\n\n"

    return res
