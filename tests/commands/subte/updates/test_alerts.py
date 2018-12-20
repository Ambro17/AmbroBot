# -*- coding: UTF-8 -*-
import pytest
from unittest.mock import call

from commands.subte.constants import SUBWAY_ICON, SUBWAY_LINE_OK
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
sample_response_no_updates = {
    'header': {
        'gtfs_realtime_version': '2.0',
        'incrementality': 0,
        'timestamp': 1545183402
    },
    'entity': []
}


@pytest.fixture()
def bot(mocker):
    return mocker.MagicMock(name='bot')


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
    (linea_alert('PM-Civico'), 'PM Civico'),
    (linea_alert('PM-Cívico'), 'PM Cívico'),
    (linea_alert('PM-Savio'), 'PM Savio'),
])
def test_get_correct_line_identifier(linea_raw, linea):
    assert _get_linea_name(linea_raw) == linea


@pytest.mark.parametrize('context, status_updates, updated_context', [
    ({}, [('A', 'something'), ('B', 'otherthing')], {'A': 'something', 'B': 'otherthing'}),
    ({'C': '123'}, [('A', 'something'), ('B', 'otherthing')], {'A': 'something', 'B': 'otherthing', 'C': '123'}),
    ({'A': '123'}, [('A', 'something')], {'A': 'something'}),
    ({'A': '123'}, [], {}),
])
def test_update_context_per_line(context, status_updates, updated_context):
    update_context_per_line(status_updates, context)
    assert context == updated_context


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
    status_updates = dict([('A', 'broken'), ('B', 'with_delays'), ('C', 'new_update')])
    mocker.patch(
        'commands.subte.updates.alerts.get_suscriptors_by_line',
        return_value=[suscriptor(id_=10), suscriptor(id_=30)]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Validate that only messages of linea C were sent to the two suscriptors.
    assert bot.send_message.call_count == 2
    assert bot.send_message.call_args_list == [
        call(chat_id=10, text=f'C | {SUBWAY_ICON}️ new_update'),
        call(chat_id=30, text=f'C | {SUBWAY_ICON}️ new_update'),
    ]


@pytest.mark.parametrize('context, status_updates, messages_sent', [
    ({'A': 'The line was broken'}, {}, 1),
    ({'A': 'The line was broken', 'B': 'Broken', 'C': 'Broken'}, {}, 3),
    ({'D': 'suspended', 'E': 'delayed'}, {'E': 'delayed'}, 1),
]
)
def test_send_update_when_line_has_resumed_normal_operation(mocker, suscriptor, context, status_updates, messages_sent):
    bot = mocker.MagicMock(name='bot')
    mocker.patch(
        'commands.subte.updates.alerts.get_suscriptors_by_line',
        return_value=[suscriptor(id_=15)]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Validate that only messages of linea C were sent to the two suscriptors.
    assert bot.send_message.call_count == messages_sent
    # assert all sent messages were sent to notify that subway line is working as expected
    assert all(['funciona con normalidad' in msg_call[1]['text'] for msg_call in bot.send_message.call_args_list])


def test_notify_normalization_and_new_updates(mocker, suscriptor, bot):
    # Test that service normalization services are sent along with updates on other line conflicts
    context = {'A': 'Broken', 'B': 'Broken', 'C': 'Broken'}
    status_updates = {'B': 'Working on fixing', 'C': 'now dead'}
    mocker.patch(
        'commands.subte.updates.alerts.get_suscriptors_by_line',
        return_value=[suscriptor(id_=1)]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Validate
    assert bot.send_message.call_count == 3
    assert bot.send_message.call_args_list == [
        call(chat_id=1, text=f'B | {SUBWAY_ICON}️ Working on fixing'),
        call(chat_id=1, text=f'C | {SUBWAY_ICON}️ now dead'),
        call(chat_id=1, text=SUBWAY_LINE_OK.format('A'))
    ]


def test_send_to_corresponding_suscriptor(bot, mocker, suscriptor):
    """Test that updates are sent to the suscriptor of that line"""
    context = {'A': 'Broken', 'B': 'Broken'}
    status_updates = {'A': 'Working', 'B': 'Working'}
    mocker.patch(
        'commands.subte.updates.alerts.get_suscriptors_by_line',
        side_effect=[
            (suscriptor(id_=1), (suscriptor(id_=2))),  # suscribers to A line
            (suscriptor(id_=10), (suscriptor(id_=11))),  # suscribers to B line
        ]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Assert updates were sent to the correct suscriptors.
    assert bot.send_message.call_count == 4
    assert bot.send_message.call_args_list == [
        call(chat_id=1, text='A | 🚆️ Working'),
        call(chat_id=2, text='A | 🚆️ Working'),
        call(chat_id=10, text='B | 🚆️ Working'),
        call(chat_id=11, text='B | 🚆️ Working')
    ]

