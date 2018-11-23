import pytest

from commands.subte.updates.alerts import _get_linea_name

sample_alerts = [
    {
        'id': 'Alert_LineaA',
        'is_deleted': False,
        'trip_update': None,
        'vehicle': None,
        'alert': {
            'active_period': [],
            'informed_entity': [{
                'agency_id': '',
                'route_id': 'LineaA',
                'route_type': 0,
                'trip': None,
                'stop_id': ''
            }],
            'cause': 2,
            'effect': 2,
            'url': None,
            'header_text': {
                'translation': [{
                    'text': 'Por obras en zona de vías: Servicio limitado entre Perú y San Pedrito.',
                    'language': 'es'
                }]
            },
            'description_text': {
                'translation': [{
                    'text': 'Por obras en zona de vías: Servicio limitado entre Perú y San Pedrito.',
                    'language': 'es'
                }]
            }
        }
    },
    {
        'id': 'Alert_PM-Civico',
        'is_deleted': False,
        'trip_update': None,
        'vehicle': None,
        'alert': {
            'active_period': [],
            'informed_entity': [{
                'agency_id': '',
                'route_id': 'PM-Civico',
                'route_type': 0,
                'trip': None,
                'stop_id': ''
            }],
            'cause': 1,
            'effect': 1,
            'url': None,
            'header_text': {
                'translation': [{
                    'text': 'Servicio interrumpido',
                    'language': 'es'
                }]
            },
            'description_text': {
                'translation': [{
                    'text': 'Servicio interrumpido',
                    'language': 'es'
                }]
            }
        }
    }
]
sample_response_full = {
    'header': {
        'gtfs_realtime_version': '2.0',
        'incrementality': 0,
        'timestamp': 1542805109
    },
    'entity': [{
        'id': 'Alert_LineaA',
        'is_deleted': False,
        'trip_update': None,
        'vehicle': None,
        'alert': {
            'active_period': [],
            'informed_entity': [{
                'agency_id': '',
                'route_id': 'LineaA',
                'route_type': 0,
                'trip': None,
                'stop_id': ''
            }],
            'cause': 2,
            'effect': 2,
            'url': None,
            'header_text': {
                'translation': [{
                    'text': 'Por obras en zona de vías: Servicio limitado entre Perú y San Pedrito.',
                    'language': 'es'
                }]
            },
            'description_text': {
                'translation': [{
                    'text': 'Por obras en zona de vías: Servicio limitado entre Perú y San Pedrito.',
                    'language': 'es'
                }]
            }
        }
    }]
}


@pytest.fixture()
def linea_alert(linea_name):
    return {
        'active_period': [],
        'informed_entity': [{
            'agency_id': '',
            'route_id': linea_name,
            'route_type': 0,
            'trip': None,
            'stop_id': ''
        }],
        'cause': 1,
        'effect': 1,
        'url': None,
        'header_text': {
            'translation': [{
                'text': 'Servicio interrumpido',
                'language': 'es'
            }]
        },
        'description_text': {
            'translation': [{
                'text': 'Servicio interrumpido',
                'language': 'es'
            }]
        }
    }


@pytest.mark.parametrize('linea_raw, linea', [
    (linea_alert('LineaA'), 'A'),
    (linea_alert('LineaB'), 'B'),
    (linea_alert('LineaC'), 'C'),
    (linea_alert('LineaD'), 'D'),
    (linea_alert('LineaE'), 'E'),
    (linea_alert('LineaH'), 'H'),
    (linea_alert('PM-Civico'), 'Premetro Civico'),
    (linea_alert('PM-Cívico'), 'Premetro Cívico'),
    (linea_alert('PM-Savio'), 'Premetro Savio'),
])
def test_get_correct_line_identifier(linea_raw, linea):
    assert _get_linea_name(linea_raw) == linea
