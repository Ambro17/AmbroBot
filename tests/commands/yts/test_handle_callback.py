from commands.yts.callback_handler import handle_callback
from commands.yts.constants import NEXT_YTS


def test_timeout_on_input_media_photo_is_retried(mocker):
    bot, update = mocker.MagicMock(), mocker.MagicMock()
    callback_mock = mocker.MagicMock()
    callback_mock.data = NEXT_YTS
    mocker.patch('path/to/getphoto', return_value=None)
    update.callback_query = callback_mock
    chat_data = {
        'context': {
        'data': [],
        'movie_number': 0,
        'movie_count': 0,
        'command': 'yts',
        'edit_original_text': True,
        }
    }
    handle_callback(bot, update, chat_data)
    bot.send_message.assert_called_with(1, text='Request for new photo timed out. Try again.')
    pass


def test_get_photo():
    
    pass


"""
    try:
        return InputMediaPhoto(image_url)
    except TimedOut:
        # Try again.
        try:
            return InputMediaPhoto(image_url)
        except TimedOut:
            return None
"""