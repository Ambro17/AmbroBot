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

# heroku doesn't have es_AR locale
days = ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')
ESP_DAY = {day_num: days[day_num] for day_num in range(7)}

FERIADOS_URL = 'http://nolaborables.com.ar/api/v2/feriados/{year}'
