import logging

import pytest
from telegram.error import TimedOut

from commands.yts.callback_handler import handle_callback
from commands.yts.constants import NEXT_YTS
from commands.yts.utils import get_photo


@pytest.fixture()
def sample_movie():
    return {
        "id": 9397,
        "url": "https://yts.am/movie/rabbit-2017",
        "imdb_code": "tt3415358",
        "title": "Rabbit",
        "title_english": "Rabbit",
        "title_long": "Rabbit (2017)",
        "slug": "rabbit-2017",
        "year": 2017,
        "rating": 6.2,
        "runtime": 0,
        "genres": ["Thriller"],
        "summary": "After a vivid dream, Maude Ashton returns to Adelaide, certain she now knows the whereabouts of her missing twin sister.",
        "description_full": "After a vivid dream, Maude Ashton returns to Adelaide, certain she now knows the whereabouts of her missing twin sister.",
        "synopsis": "After a vivid dream, Maude Ashton returns to Adelaide, certain she now knows the whereabouts of her missing twin sister.",
        "yt_trailer_code": "o-kjbU8lWL8",
        "language": "English",
        "mpa_rating": "",
        "background_image": "https://yts.am/assets/images/movies/rabbit_2017/background.jpg",
        "background_image_original": "https://yts.am/assets/images/movies/rabbit_2017/background.jpg",
        "small_cover_image": "https://yts.am/assets/images/movies/rabbit_2017/small-cover.jpg",
        "medium_cover_image": "https://yts.am/assets/images/movies/rabbit_2017/medium-cover.jpg",
        "large_cover_image": "https://yts.am/assets/images/movies/rabbit_2017/large-cover.jpg",
        "state": "ok",
        "torrents": [{
            "url": "https://yts.am/torrent/download/035AF68CEF3D90223BD6B0AF7749D758E3758C32",
            "hash": "035AF68CEF3D90223BD6B0AF7749D758E3758C32",
            "quality": "720p",
            "seeds": 288,
            "peers": 207,
            "size": "845.33 MB",
            "size_bytes": 886392750,
            "date_uploaded": "2018-10-21 08:43:31",
            "date_uploaded_unix": 1540104211
        }, {
            "url": "https://yts.am/torrent/download/73FE4BD77A20FEE5185FC509A4F5BD6B4B814588",
            "hash": "73FE4BD77A20FEE5185FC509A4F5BD6B4B814588",
            "quality": "1080p",
            "seeds": 117,
            "peers": 134,
            "size": "1.6 GB",
            "size_bytes": 1717986918,
            "date_uploaded": "2018-10-21 10:14:26",
            "date_uploaded_unix": 1540109666
        }],
        "date_uploaded": "2018-10-21 08:43:31",
        "date_uploaded_unix": 1540104211
    }


def test_get_photo_retry_works(mocker, caplog):
    caplog.set_level(logging.INFO)
    mocker.patch('commands.yts.utils.InputMediaPhoto', side_effect=[TimedOut, 'photo_url'])
    assert get_photo('url_img') == 'photo_url'
    assert 'Retrying..' in caplog.text

def test_get_photo_returns_none_on_timeout(mocker, caplog):
    caplog.set_level(logging.INFO)
    mocker.patch('commands.yts.utils.InputMediaPhoto', side_effect=TimedOut)
    assert get_photo('url_img') is None
    assert 'Retry Failed.' in caplog.text


def test_handle_callback_with_timeout_sends_message(mocker, sample_movie, caplog):
    bot, update = mocker.MagicMock(), mocker.MagicMock()
    update.callback_query.data = NEXT_YTS
    mocker.patch('commands.yts.utils.InputMediaPhoto', side_effect=TimedOut)
    chat_data = {
        'context': {
            'data': [sample_movie, sample_movie],
            'movie_number': 0,
            'movie_count': 1,
            'command': 'yts',
            'edit_original_text': True
        }
    }
    caplog.set_level(logging.INFO)
    handle_callback(bot, update, chat_data)
    assert bot.send_message.call_count == 1
    assert bot.send_message.call_args[1]['text'] == 'Request for new photo timed out. Try again.'
    assert "Could not build InputMediaPhoto from url" in caplog.text
