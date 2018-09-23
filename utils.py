
LN_CURRENCY_CODES = {
    'DLRBILL': 'Dolar Minorista',
    'CMPES': 'Real x Pesos',
    'CMUSD': 'Real x Dolar',
    'EURPES': 'Euro x Pesos',
    'EURUSD': 'Euro x Dolar',
    'MEXPES': 'Pesos x Peso Mex.',
    'MEXUSD': 'Peso Mex. x Dolar',
    'CHIMEX': 'Pesos x Peso Chile',
    'CHIUSD': 'Peso Chile x Dolar',
    'YENPES': 'Pesos x Yen',
    'YENUSD': 'Yen x Dolar',
    'LIBPES': 'Libras x Peso ',
    'LIBUSD': 'Libra x Dolar',
    'URUPES': 'PURU x Pesos',
    'URUUSD': 'PURU x Dolar',
    'DBNA': 'Dolar Banco Nacion',
}

def get_moneda(moneda, monedas):
    return next(
        (m for m in monedas
        if m['papel'] == moneda), None)

def format_moneda_output(moneda_dict):
    TABLE = "{:^10} {:^10} {:^10}"
    HEADER = TABLE.format("Moneda", "Compra", "Venta")
    DATA = TABLE.format(
        moneda_dict['papel'],
        moneda_dict['venta'],
        moneda_dict['compra']
    )
    return HEADER + '\n' + DATA