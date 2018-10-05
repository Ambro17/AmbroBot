from utils.command_utils import pretty_print_dolar


def dolarhoy_callback(banco_data, banco):
    """Shows only the info of desired banco from banco_data"""
    # Maybe we need some asociation between banco callback_data and the name of the key on the dict.
    # -> For now, callback data will match banco_data key, but this may be error prone (can we avoid that, tho?)
    # Filtrar en el dict la entrada que quiero o crear otra
    requested_banco = {k:v for k,v in banco_data.items() if k == banco}
    if requested_banco:
        return pretty_print_dolar(requested_banco)
    elif banco == 'Todos':
        return pretty_print_dolar(banco_data)
