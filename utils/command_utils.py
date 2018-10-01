import logging
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache

logger = logging.getLogger(__name__)


# Generic utils
def monospace(text):
    return f'```\n{text}\n```'


def normalize(text, limit=11):
    """Trim and append . if text is too long. Else return it unmodified"""
    return f'{text[:limit]}.' if len(text) > limit else text


class Soupifier(object):
    """Implements a cache with expiration for the given urls.

    Each url is a key of the cache dict. Its value is the soupified url.
    During n minutes, the value will be remembered, after that it will be
    removed and the request will happen again
    """

    def __init__(self, minutes_to_live=5, timeout=2):
        self.cache = TTLCache(maxsize=10, ttl=60*minutes_to_live)
        self.timeout = timeout

    def soupify(self, url):
        try:
            soup = self.cache[url]
            logger.info("Cached value for %s", url)
            return soup
        except KeyError:
            logger.info("Caché for %s expired. Updating.", url)
            self.cache[url] = soupify_url(url, timeout=self.timeout)
            return self.cache[url]

# To be used after profiling bot use
soup = Soupifier()
_soupify_url = soup.soupify

def soupify_url(url, timeout=2):
    """Given a url returns a BeautifulSoup object"""
    r = requests.get(url, timeout=timeout)
    r.encoding = 'utf-8'
    if r.status_code == 200:
        return BeautifulSoup(r.text, 'lxml')
    else:
        raise ConnectionError(f'{url} did not respond.')



# Helper functions for /posiciones
def parse_posiciones(tabla, posiciones=None):
    # #, Equipo, pts y PJ
    posiciones = int(posiciones[0]) if posiciones else 5
    LIMIT = 4
    headers = [th.text for th in tabla.thead.find_all('th')[:LIMIT]]
    res = [
        [normalize(r.text) for r in row.find_all('td')[:LIMIT]]
        for row in
        tabla.tbody.find_all('tr')[:posiciones]]
    res.insert(0, headers)
    return res

# Helper function for /posiciones
def prettify_table_posiciones(info):
    try:
        return monospace('\n'.join(
            '{:2} | {:12} | {:3} | {:3}'.format(*team_stat) for
            team_stat in info
        ))
    except Exception:
        logger.error(f"Error Prettying info {info}")
        return 'No te entiendo..'


# Helper func for /subte
def format_estado_de_linea(info_de_linea):
    linea, estado = info_de_linea
    if estado.lower() == 'normal':
        estado = '✅'
    else:
        estado = f'⚠ {estado} ⚠'
    return f'{linea} {estado}'


# Helper func for dolar_hoy
def get_cotizaciones(response_soup):
    """Returns a dict of cotizaciones with banco as keys and exchange rate as value.

    {
        "Banco Nación": {
            "Compra": "30.00",
            "Venta": "32.00",
        },
        "Banco Galicia": {
            "Compra": "31.00",
            "Venta": "33.00",
        }
    }

    """
    cotizaciones = defaultdict(dict)
    for table in response_soup:
        # Get cotizaciones
        for row_cotizacion in table.tbody.find_all('tr'):
            banco, compra, venta = (item.get_text() for item in row_cotizacion.find_all('td'))
            banco = banco.replace('Banco ', '')
            cotizaciones[banco]['compra'] = compra
            cotizaciones[banco]['venta'] = venta

    return cotizaciones


# Helper func for dolar_hoy
def pretty_print_dolar(cotizaciones):
    """Returns dolar rates separated by newlines and with code markdown syntax.
    ```
    Banco Nacion  | $30.00 | $40.00
    Banco Galicia | $30.00 | $40.00
                   ...
    ```
    """
    MONOSPACE = "```\n{}\n```"
    return MONOSPACE.format('\n'.join(
            "{:8} | {:7} | {:7}".format(normalize(banco, limit=7), valor['compra'], valor['venta'])
            for banco, valor in cotizaciones.items()
        ))


# Helper func for partido
def info_de_partido(partido):
    logo = partido.img.attrs['src']
    fecha = partido.find('div', {'class': 'temp'}).text
    hora, tv, estadio, arbitro =[p.text for p in partido.find_all('p') if p.text]
    return logo, fecha, hora, tv, estadio, arbitro
