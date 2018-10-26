from telegram.error import TimedOut
from commands.yts.utils import get_photo

def test_get_photo(mocker):
    mocker.patch('commands.yts.utils.InputMediaPhoto', side_effect=[TimedOut, 'photo_url'])
    assert get_photo('url_img') == 'photo_url'