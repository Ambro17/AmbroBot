import logging

from utils.command_utils import normalize, monospace

logger = logging.getLogger(__name__)


def parse_posiciones(tabla, posiciones=None):
    posiciones = int(posiciones[0]) if posiciones else 10
    LIMIT = 4
    # ['#', 'Equipo', 'Pts', 'PJ']
    headers = [th.text for th in tabla.thead.find_all('th')[:LIMIT]]
    a = []
    for row in tabla.tbody.find_all('tr')[:posiciones]:
        b = [normalize(r.text) for r in row.find_all('td')[:LIMIT]]
        a.append(b)
    a.insert(0, headers)
    return a


def prettify_table_posiciones(info):
    try:
        return monospace(
            '\n'.join(
                '{:2} | {:12} | {:3} | {:3}'.format(*team_stat) for team_stat in info
            )
        )
    except Exception:
        logger.error(f"Error Prettying info {info}")
        return 'No te entiendo..'
