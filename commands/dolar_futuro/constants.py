import re
from collections import namedtuple

month_name = {
    1: 'Ene',
    2: 'Feb',
    3: 'Mar',
    4: 'Abr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Ago',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dic',
}
DOLAR_REGEX = re.compile(r'DLR(\d{2})(\d{4})')  # DLRmmYYYY
Contrato = namedtuple('Contrato', ['mes', 'año', 'valor'])
