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

FERIADOS_URL = 'http://nolaborables.com.ar/api/v2/feriados/{year}'
