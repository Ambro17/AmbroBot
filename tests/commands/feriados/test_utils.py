import pytest
from commands.feriados.utils import feriados_from_string

one_day = '1. Año nuevo. '
two_days = '12 y 13. Carnaval. '
other_two_days = '30 y 31. Pascuas Judías. '
four_days = '1, 5, 6 y 7. Pascuas Judías. '
extra_nums_on_the_end = '20. Paso a la Inmortalidad del Gral. José de San Martín (17/8). '
yet_another_example = '9, 10 y 11. Año Nuevo Judío. Día no laborable'

@pytest.mark.parametrize('feriado_desc, expected_feriados', [
    (one_day, {1: ('Año nuevo.', 'tipo_feriado')}),
    (two_days, {
        12: ('Carnaval.', 'tipo_feriado'),
        13: ('Carnaval.', 'tipo_feriado'),
    }),
    (four_days, {
        1: ('Pascuas Judías.', 'tipo_feriado'),
        5: ('Pascuas Judías.', 'tipo_feriado'),
        6: ('Pascuas Judías.', 'tipo_feriado'),
        7: ('Pascuas Judías.', 'tipo_feriado'),
    }),
    (extra_nums_on_the_end, {
        20: ('Paso a la Inmortalidad del Gral. José de San Martín (17/8).', 'tipo_feriado'),
    }),
    (yet_another_example, {
        9: ('Año Nuevo Judío. Día no laborable', 'tipo_feriado'),
        10: ('Año Nuevo Judío. Día no laborable', 'tipo_feriado'),
        11: ('Año Nuevo Judío. Día no laborable', 'tipo_feriado')
    }),
])
def test_parse_days(feriado_desc, expected_feriados):
    assert feriados_from_string(feriado_desc, 'tipo_feriado') == expected_feriados