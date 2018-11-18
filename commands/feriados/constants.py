import re

meses = (
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
)
month_num = {mes: mes_number for mes, mes_number in zip(meses, range(1, 13))}

month_names = {mes_number: mes for mes, mes_number in month_num.items()}

DAYS_REGEX = re.compile(r'(\d+)')

YEAR_2019 = '2019'
FERIADOS_URL = 'https://www.argentina.gob.ar/interior/feriados'
FERIADOS_2019_URL = 'https://www.argentina.gob.ar/interior/feriados2019'
