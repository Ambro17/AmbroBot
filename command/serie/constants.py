import re
from collections import namedtuple

# Callback data constants
SERIE = r'SERIE_'
LATEST_EPISODES = SERIE + 'LATEST_EPISODES'
LOAD_EPISODES = SERIE + 'LOAD_EPISODES'
GO_BACK_TO_MAIN = SERIE + 'GO_TO_MAIN_RESULT'
SEASON_T = SERIE + 'SEASON_{}'
EPISODE_T = SERIE + 'EPISODE_{}'

# Regex to find season and episode data
SEASON_REGEX = re.compile(r'S(\d{1,})E(\d{1,})')  # S01E15
ALT_SEASON_REGEX = re.compile(r'(\d{1,})x(\d{1,})')  # 1x15
EPISODE_PATTERNS = [SEASON_REGEX, ALT_SEASON_REGEX]

# Indexes to build Episode from html row
NAME, SIZE, RELEASED, SEEDS = 0, 2, 3, 4
MAGNET, TORRENT = 0, 1

# Episode representation after parsing eztv web
Episode = namedtuple('Episode', ['name', 'season', 'episode', 'magnet', 'torrent', 'size', 'released', 'seeds'])

# eztv api error messages
EZTV_API_ERROR = "EZTV api failed to respond with latest torrents. Try 'Load all episodes' option and look for latest episode."
EZTV_NO_RESULTS = ("Eztv api did not return any result for the series❕\nPlease notice it's still in beta mode 🐣\n"
                   "You can try loading all episodes and manually searching the latest.")