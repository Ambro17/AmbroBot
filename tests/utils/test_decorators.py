import pytest

from utils.decorators import handle_empty_arg


@pytest.fixture()
def func():
    def helper_func(bot, update, a, b):
        return bot, update, a, b

    return helper_func


@pytest.fixture()
def fake_func_with_kwargs():
    def helper_func(bot, update, a, b, c=3, d=4):
        return bot, update, a, b

    return helper_func


@pytest.fixture()
def fake_func_required_kwarg(bot, update, my_kwarg=1):
    return bot, update, my_kwarg


@pytest.fixture()
def update_object(mocker):
    return mocker.MagicMock(name='update')


@pytest.fixture()
def bot_object(mocker):
    return mocker.MagicMock(name='bot')


EMPTY = ''


@pytest.mark.parametrize('func', [func(), fake_func_with_kwargs()])
def test_handle_empty_arg_decorator(bot_object, update_object, func):
    # Pre-Check that function just returns its args
    assert func(bot_object, update_object, 'a', 'b') == (bot_object, update_object, 'a', 'b')

    # Create decorator with custom values and decorate function to output message if required_param is empty
    decorated_func = handle_empty_arg(
        required_params=('a',), error_message='falto un arg', parse_mode='some_parse_mode'
    )(func)

    # Execute decorated func
    result = decorated_func(bot_object, update_object, EMPTY, 'b')

    # Assert function was not executed and instead reply_text was called
    assert update_object.effective_message.reply_text.call_count == 1
    update_object.effective_message.reply_text.assert_called_once_with(
        'falto un arg', parse_mode='some_parse_mode'
    )

    # Check that function *is* called if required argument is not empty
    second_result = decorated_func(bot_object, update_object, 'not_empty', 'b')
    # Function returns its arguments, as it did before decorating.
    assert second_result == (bot_object, update_object, 'not_empty', 'b')
    # reply_text was called only once, on the previous call. But not this time. Thus, call_count is still 1
    assert update_object.effective_message.reply_text.call_count == 1

# TODO: Agregar test que simula como se pasa chat_data. Test paso pero implementacion fallo.
