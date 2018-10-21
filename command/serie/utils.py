import logging
from collections import namedtuple, defaultdict
from functools import lru_cache

import requests
from bs4 import BeautifulSoup

from command.serie.constants import (
    NAME,
    EPISODE_PATTERNS,
    MAGNET,
    TORRENT,
    SIZE,
    RELEASED,
    SEEDS,
    Episode)

logger = logging.getLogger(__name__)

@lru_cache(5)
def prettify_serie(name, rating, overview, start_date):
    if start_date:
        name = f"{name} ({start_date})"
    stars = int(rating // 2)
    rating = f"{'⭐'*stars} ~ {rating}"
    return '\n'.join((name, rating, overview))


@lru_cache(20)
def get_torrents_by_id(imdb_id, limit=None):
    """Request torrents from api and return a minified torrent representation."""
    try:
        r = requests.get('https://eztv.ag/api/get-torrents', params={'imdb_id': imdb_id, 'limit': limit})
        torrents = sorted(
            r.json()['torrents'],
            key=lambda d: (d['season'], d['episode'])
        )
    except KeyError:
        logger.info("No torrents in eztv api for this serie. Response %s", r.json())
        return None
    except Exception:
        logger.exception("Error requesting torrents for %s", imdb_id)
        return None

    return _minify_torrents(torrents)


def _minify_torrents(torrents):
    """Returns a torrent name, url, seeds and size from json response"""
    for torrent in torrents:
        try:
            MB = 1024 * 1024
            size_float = int(torrent['size_bytes']) / MB
            size = f"{size_float:.2f}"
            torrent = torrent['title'], torrent['torrent_url'], torrent['seeds'], size
        except Exception:
            logger.exception("Error parsing torrent from eztv api. <%s>", torrent)
            continue
        else:
            yield torrent


def prettify_torrents(torrents):
    return '\n'.join(
        prettify_torrent(*torrent) for torrent in torrents
        if prettify_torrent(torrent)
    )


def prettify_torrent(name, torrent_url, seeds, size):
    return (
        f"🏴‍☠️ [{name}]({torrent_url})\n"
        f"🌱 Seeds: {seeds} | 🗳 Size: {size}MB\n"
    )


@lru_cache(20)
def get_all_seasons(series_name):
    """Parses eztv search page in order to return all episodes of a given series.

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

        # First and last cell contain useless info (link with info and forum link)
        torrent = torrent.find_all('td')[1:-1]
        links = torrent[1].find_all('a')
        name = torrent[NAME].text.strip()

        # Filter fake results that include series name but separated between other words.
        # For example, a query for The 100 also returns '*The* TV Show S07E00 Catfish Keeps it *100*' which we don't want
        if not series_name.lower() in name.lower():
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
    series_query = series_name.replace(' ', '-')
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

    logger.info("'%s' series episodes retrieved. Seasons: %s", series_name, series_episodes.keys())
    return series_episodes


def prettify_episodes(episodes, header=None):
    episodes = '\n\n'.join(
        prettify_episode(ep) for ep in episodes
    )
    if header:
        episodes = '\n'.join((header, episodes))

    return episodes

def prettify_episode(ep):
    """Episodes have name, season, episode, torrent, magnet, size, seeds and released attributes"""
    return (
        f"[{ep.name}]({ep.torrent})\n"
        f"🌱 Seeds: {ep.seeds}\n"
        f"🗳 Size: {ep.size}MB\n"
    )
