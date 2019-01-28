import logging
from collections import defaultdict
from functools import lru_cache
from operator import attrgetter

import requests
from bs4 import BeautifulSoup

from commands.serie.constants import (
    NAME,
    EPISODE_PATTERNS,
    MAGNET,
    TORRENT,
    SIZE,
    RELEASED,
    SEEDS,
    Episode,
    EZTVEpisode,
)
from utils.utils import monospace

logger = logging.getLogger(__name__)


def rating_stars(rating):
    """Transforms int rating into stars with int"""
    stars = int(rating // 2)
    rating_stars = f"{'⭐'*stars} ~ {rating}"
    return rating_stars


@lru_cache(5)
def prettify_serie(name, rating, overview, start_date):
    if start_date:
        name = f"{name} ({start_date})"
    stars = rating_stars(rating)
    return '\n'.join((name, stars, overview))


@lru_cache(20)
def request_eztv_torrents_by_imdb_id(imdb_id, limit=None):
    """Request torrents from api and return a minified torrent representation.

    A torrent is a tuple of (title, url, seeds, size)
    """
    try:
        r = requests.get(
            'https://eztv.ag/api/get-torrents',
            params={'imdb_id': imdb_id, 'limit': limit},
        )
        torrents = r.json()['torrents']
    except KeyError:
        logger.info("No torrents in eztv api for this serie. Response %s", r.json())
        return None
    except Exception:
        logger.exception("Error requesting torrents for %s", imdb_id)
        return None

    return parse_torrents(torrents)


def _read_season_episode_from_title(title):
    for pattern in EPISODE_PATTERNS:
        match = pattern.search(title)
        if match:
            season, episode = match.groups()
            return season, episode
    else:
        return 0, 0


def parse_torrents(torrents):
    """Returns a torrent name, url, seeds and size from json response"""
    parsed_torrents = []
    for torrent in torrents:
        try:
            MB = 1024 * 1024
            size_float = int(torrent['size_bytes']) / MB
            size = f"{size_float:.2f}"
            title = torrent['title']
            season, episode = _read_season_episode_from_title(title)
            parsed_torrents.append(
                EZTVEpisode(
                    name=title,
                    season=season,
                    episode=episode,
                    torrent=torrent['torrent_url'],
                    seeds=torrent['seeds'],
                    size=size,
                )
            )
        except Exception:
            logger.exception("Error parsing torrent from eztv api. <%s>", torrent)
            continue

    # Order torrents to from latest to oldest
    ordered_torrents = sorted(
        parsed_torrents, key=attrgetter('season', 'episode'), reverse=True
    )
    # Make it hashable so lru_cache can remember it and avoid reloading.
    ordered_torrents = tuple(ordered_torrents)

    return ordered_torrents


@lru_cache(5)
def prettify_torrents(torrents, limit=5):
    return '\n'.join(prettify_torrent(torrent) for torrent in torrents[:limit])


def prettify_torrent(torrent):
    return (
        f"[{torrent.name}]({torrent.torrent})\n"
        f"🌱 Seeds: {torrent.seeds} | 🗳 Size: {torrent.size}MB\n"
    )


@lru_cache(20)
def get_all_seasons(series_name, raw_user_query):
    """Parses eztv search page in order to return all episodes of a given series.

    Args:
        series_name: Full series name as it is on tmdb
        raw_user_query: The user query, with possible typos or the incomplete series_name

    Unlike get_latest_episodes handler function, this does not communicate directly
    with the eztv api because the api is in beta mode and has missing season and episode info
    for many episodes.
    In order to present the series episodes in an orderly manner, we need to rely on
    that information consistency and completeness. Neither of those requirements
    are satisfied by the api. That's why we parse the web to get consistent results.
    Quite a paradox..


    Returns:
        {
            1: # season
                1: [ # episode
                    {Episode()},
                    {Episode()},
                    ...
                ],
                2: [
                    {Episode()},
                    {Episode()},
                    ...
                ]
            2:
                1: [
                    {Episode()},
                    {Episode()},
                    ...
                ],
                ...
            ...
        }

    """
    series_episodes = defaultdict(lambda: defaultdict(list))

    def get_link(links, key):
        try:
            link = links[key]['href']
        except (IndexError, AttributeError):
            link = ''

        return link

    def get_episode_info(torrent):
        """Parse html to return an episode data.

        Receives an html row, iterates its tds
        (leaving the first and last values out).
        and returns an episode namedtuple
        """

        # First cell contain useless info (link with info)
        torrent = torrent.find_all('td')[1:]
        links = torrent[1].find_all('a')
        name = torrent[NAME].text.strip()

        # Filter fake results that include series name but separated between other words.
        # For example, a query for The 100 also returns '*The* TV Show S07E00 Catfish
        # Keeps it *100*' which we don't want. We also use the raw_user_query
        # because sometimes the complete name from tmdb is not the same name used on eztv.
        if (
                not series_name.lower() in name.lower()
                and not raw_user_query.lower() in name.lower()
        ):
            # The tradeoff is that we don't longer work for series with typos. But it's better than giving fake results.
            logger.info(f"Fake result '{name}' for query '{series_name}'")
            return None

        for pattern in EPISODE_PATTERNS:
            match = pattern.search(name)
            if match:
                season, episode = match.groups()
                break
        else:
            # No season and episode found
            logger.info(f"Could not read season and episode data from torrent '{name}'")
            return None

        return Episode(
            name=name.replace('[', '').replace(']', ''),
            season=int(season),
            episode=int(episode),
            magnet=get_link(links, MAGNET),
            torrent=get_link(links, TORRENT),
            size=torrent[SIZE].text.strip(),
            released=torrent[RELEASED].text.strip(),
            seeds=torrent[SEEDS].text.strip(),
        )

    # Parse episodes from web
    series_query = raw_user_query.replace(' ', '-')
    r = requests.get("https://eztv.ag/search/{}".format(series_query))
    soup = BeautifulSoup(r.text, 'lxml')
    torrents = soup.find_all('tr', {'class': 'forum_header_border'})

    # Build the structured dict
    for torrent in torrents:
        episode_info = get_episode_info(torrent)
        if not episode_info:
            # We should skip torrents if they don't belong to a season
            continue

        season, episode = episode_info.season, episode_info.episode
        # Attach the episode under the season key, under the episode key, in a list of torrents of that episode
        series_episodes[season][episode].append(episode_info)

    logger.info(
        "'%s' series episodes retrieved. Seasons: %s",
        series_name,
        series_episodes.keys(),
    )
    return series_episodes


def prettify_episodes(episodes, header=None):
    episodes = '\n\n'.join(prettify_episode(ep) for ep in episodes)
    if header:
        episodes = '\n'.join((header, episodes))

    return episodes


def prettify_episode(ep):
    """Episodes have name, season, episode, torrent, magnet, size, seeds and released attributes"""
    # Some episodes do not have a torrent download. But they do have a magnet link.
    # Since magnet links are not clickable on telegram, we leave them as a fallback.
    if ep.torrent:
        header = f"[{ep.name}]({ep.torrent})\n"
    elif ep.magnet:
        header = f"Magnet: {monospace(ep.magnet)}"
    else:
        header = 'No torrent nor magnet available for this episode.'

    return f"{header}" f"🌱 Seeds: {ep.seeds} | 🗳 Size: {ep.size or '-'}"
