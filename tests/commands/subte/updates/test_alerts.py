# -*- coding: UTF-8 -*-
import pytest
from unittest.mock import call

from commands.subte.constants import SUBWAY_ICON, SUBWAY_LINE_OK, SUBWAY_STATUS_OK
from commands.subte.updates.alerts import notify_suscribers, subte_updates_cron
from commands.subte.updates.utils import _get_linea_name

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
def job(mocker):
    job = mocker.MagicMock(name='job')

    def inner(context):
        job.context = context
        return job

    return inner


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
        'commands.subte.updates.utils.get_suscriptors_by_line',
        return_value=[suscriptor(id_=10), suscriptor(id_=30)]
    )

    # Exercise
    notify_suscribers(bot, status_updates, context)

    # Validate that only messages of linea C were sent to the two suscriptors.
    assert bot.send_message.call_count == 2
    assert bot.send_message.call_args_list == [
        call(chat_id=10, text=f'C | {SUBWAY_ICON}️ new_update'),
        call(chat_id=30, text=f'C | {SUBWAY_ICON}️ new_update')
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
        'commands.subte.updates.utils.get_suscriptors_by_line',
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
        'commands.subte.updates.utils.get_suscriptors_by_line',
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
        'commands.subte.updates.utils.get_suscriptors_by_line',
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


@pytest.mark.parametrize('context, status_update, send_msg_calls', [
    (
            # From normal to one incident
            {}, {'A': 'update'},
            [
                call(chat_id='@subtescaba', text='A | ⚠️ update'),
                call(chat_id=2, text='A | 🚆️ update')
            ]
    ),
    (
            # The incident was solved
            {'A': 'broken'}, {},
            [
                call(chat_id='@subtescaba', text=SUBWAY_STATUS_OK),
                call(chat_id=2, text=SUBWAY_LINE_OK.format('A'))
            ]
    ),
    (
            # From normal to two incidents
            {}, {'B': 'b_update', 'C': 'c_update'},
            [
                call(chat_id='@subtescaba', text='B | ⚠️ b_update\nC | ⚠️ c_update'),
                call(chat_id=2, text='B | 🚆️ b_update'),
                call(chat_id=2, text='C | 🚆️ c_update')
            ]
    ),
    (
            # All incidents were solved
            {'A': 'broken', 'B': 'broken'}, {},
            [
                call(chat_id='@subtescaba', text='✅ Todos los subtes funcionan con normalidad'),
                call(chat_id=2, text=SUBWAY_LINE_OK.format('A')),
                call(chat_id=2, text=SUBWAY_LINE_OK.format('B'))
            ]
    ),
    (
            # Incident description changed
            {'A': 'status'}, {'A': 'update_changed'},
            [
                call(chat_id='@subtescaba', text='A | ⚠️ update_changed'),
                call(chat_id=2, text='A | 🚆️ update_changed')
            ]
    ),
    (
            # First line still broken, B Fixed
            {'A': 'broken', 'B': 'delayed'}, {'A': 'broken'},
            [
                call(chat_id='@subtescaba', text='A | ⚠️ broken'),
                call(chat_id=2, text='✅ La linea B funciona con normalidad')
            ]
    ),
    (
            # First line still broken, B changed status
            {'A': 'broken', 'B': 'suspended'}, {'A': 'fixed', 'B': 'resumed'},
            [
                call(chat_id='@subtescaba', text='A | ⚠️ fixed\nB | ⚠️ resumed'),
                call(chat_id=2, text='A | 🚆️ fixed'),
                call(chat_id=2, text='B | 🚆️ resumed'),
            ]
    ),
    (
        # First line still broken, B changed status
        {'A': 'broken', 'B': 'broken', 'C': 'broken', 'D': 'broken', 'E': 'broken', 'H': 'broken'},
        {'A': 'fixed', 'B': 'fixed', 'C': 'fixed', 'D': 'fixed', 'E': 'fixed', 'H': 'fixed'},
        [
            call(chat_id='@subtescaba',
                 text='A | ⚠️ fixed\nB | ⚠️ fixed\nC | ⚠️ fixed\nD | ⚠️ fixed\nE | ⚠️ fixed\nH | ⚠️ fixed'),
            call(chat_id=2, text='A | 🚆️ fixed'),
            call(chat_id=2, text='B | 🚆️ fixed'),
            call(chat_id=2, text='C | 🚆️ fixed'),
            call(chat_id=2, text='D | 🚆️ fixed'),
            call(chat_id=2, text='E | 🚆️ fixed'),
            call(chat_id=2, text='H | 🚆️ fixed'),
        ]
    )
])
def test_subte_updates_cron(mocker, bot, job, suscriptor, context, status_update, send_msg_calls):
    mocker.patch('commands.subte.updates.alerts.check_update', return_value=status_update)
    mocker.patch('commands.subte.updates.utils.get_suscriptors_by_line', return_value=[suscriptor(id_=2)])
    mocker.patch('commands.subte.updates.utils.random.choice', return_value='⚠')  # Avoid random icon to ease testing

    job = job(context)
    subte_updates_cron(bot, job)
    assert bot.send_message.call_args_list == send_msg_calls
