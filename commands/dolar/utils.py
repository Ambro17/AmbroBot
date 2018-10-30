from collections import defaultdict

from utils.command_utils import monospace, normalize


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
            banco, compra, venta = (
                item.get_text() for item in row_cotizacion.find_all('td')
            )
            banco = banco.replace('Banco ', '')
            cotizaciones[banco]['compra'] = compra
            cotizaciones[banco]['venta'] = venta

    return cotizaciones


def pretty_print_dolar(cotizaciones, limit=7):
    """Returns dolar rates separated by newlines and with code markdown syntax.
    ```
    Banco Nacion  | $30.00 | $40.00
    Banco Galicia | $30.00 | $40.00
                   ...
    ```
    """
    return monospace(
        '\n'.join(
            "{:8} | {:7} | {:7}".format(
                normalize(banco, limit), valor['compra'], valor['venta']
            )
            for banco, valor in cotizaciones.items()
        )
    )
