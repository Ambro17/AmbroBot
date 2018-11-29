from collections import namedtuple
import logging

from telegram import InputMediaPhoto
from telegram.error import TimedOut

from commands.serie.utils import rating_stars
from utils.utils import normalize

Torrent = namedtuple('Torrent', ['url', 'size', 'seeds', 'quality'])

logger = logging.getLogger(__name__)


def get_minimal_movie(movie, trim_description=True):
    """Return image, title, synopsis, and Torrents from a movie."""
    title = movie['title_long']
    imdb = movie['imdb_code']
    yt_trailer = movie['yt_trailer_code']
    if trim_description:
        synopsis = normalize(movie['synopsis'], limit=150, trim_end='..')
    else:
        synopsis = movie['synopsis']

    rating = movie['rating']
    image = movie['large_cover_image']
    return title, synopsis, rating, imdb, yt_trailer, image


def get_torrents(movie):
    return [get_torrent(torrent) for torrent in movie['torrents']]


def prettify_yts_movie(title, synopsis, rating):
    # Add torrents as optional download buttons?
    message = f"{title}\n{rating_stars(rating)}\n{synopsis}\n"
    return message


def get_torrent(torrent):
    """Tranforms
    {
        "url": "https://yts.am/torrent/download/035AF68CEF3D90223BD6B0AF7749D758E3758C32",
        "hash": "035AF68CEF3D90223BD6B0AF7749D758E3758C32",
        "quality": "720p",
        "seeds": 288,
        "peers": 207,
        "size": "845.33 MB",
        "size_bytes": 886392750,
        "date_uploaded": "2018-10-21 08:43:31",
        "date_uploaded_unix": 1540104211
    }
    into Torrent namedtuple with only url, size, seeds and quality
    """
    return Torrent(
        url=torrent['url'],
        size=torrent['size'],
        seeds=torrent['seeds'],
        quality=torrent['quality'],
    )


def prettify_torrent(movie_name, torrent):
    """Pretty print a Torrent namedtuple"""
    return (
        f"[{movie_name}]({torrent.url})\n"
        f"🌱 Seeds: {torrent.seeds}\n"
        f"🗳 Size: {torrent.size}\n"
        f"🖥 Quality: {torrent.quality}\n"
    )


def get_photo(image_url):
    """Build InputMediaPhoto from image url"""
    try:
        return InputMediaPhoto(image_url)
    except TimedOut:
        logger.info('Request for photo from %s timed out.', image_url)
        logger.info('Retrying..')
        try:
            return InputMediaPhoto(image_url)
        except TimedOut:
            logger.info('Retry Failed.')
            return None
