from commands.dolar.utils import pretty_print_dolar


def dolarhoy_callback(banco_data, banco):
    """Shows only the info of desired banco from banco_data"""
    requested_banco = {k: v for k, v in banco_data.items() if k == banco}
    if requested_banco:
        return pretty_print_dolar(requested_banco)
    elif banco == 'Todos':
        return pretty_print_dolar(banco_data)
