def format_estado_de_linea(info_de_linea):
    linea, estado = info_de_linea
    if estado.lower() == 'normal':
        estado = '✅'
    else:
        estado = f'⚠ {estado} ⚠'
    return f'{linea} {estado}'
