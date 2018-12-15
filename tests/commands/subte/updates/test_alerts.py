import pytest
from unittest.mock import call

from commands.subte.updates.alerts import _get_linea_name, notify_suscribers, update_context_per_line

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


@pytest.fixture()
def suscriptor(mocker):
    def inner(id_):
        user = mocker.MagicMock(name='user')
        user.user_id = id_
        return user

    return inner


def test_dont_send_message_if_linea_status_has_not_changed(mocker, suscriptor):
    """Test that if context has already the line status, no new message is sent."""
    # Setup
    bot = mocker.MagicMock(name='bot')
    context = {'A': 'broken', 'B': 'with_delays'}
    status_updates = [('A', 'broken'), ('B', 'with_delays'), ('C', 'new_update')]
    mocker.patch(
        'commands.subte.updates.alerts.get_suscriptors_by_line',
        return_value=[suscriptor(id_=10), suscriptor(id_=30)]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Validate
    assert bot.send_message.call_count == 2
    send_message_calls = [
        call(chat_id=10, text='C | 🚇 new_update'),
        call(chat_id=30, text='C | 🚇 new_update')
    ]
    bot.send_message.assert_has_calls(send_message_calls)


@pytest.mark.parametrize('context, status_updates, updated_context', [
    ({}, [('A', 'something'), ('B', 'otherthing')], {'A': 'something', 'B': 'otherthing'}),
    ({'C': '123'}, [('A', 'something'), ('B', 'otherthing')], {'A': 'something', 'B': 'otherthing', 'C': '123'}),
    ({'A': '123'}, [('A', 'something')], {'A': 'something'}),
])
def test_update_context_per_line(context, status_updates, updated_context):
    update_context_per_line(status_updates, context)
    assert context == updated_context
