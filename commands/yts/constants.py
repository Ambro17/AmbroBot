# CallbackQuery matchers
import re

YTS = r'YTS_'
NEXT_YTS = YTS + 'NEXT'
YTS_TORRENT = YTS + 'TORRENT'
YTS_FULL_DESC = YTS + 'DESCRIPTION'

IMDB_LINK = 'https://www.imdb.com/title/{}'
YT_LINK = 'https://www.youtube.com/watch?v={}'

MEDIA_CAPTION_LIMIT = 1024

YTS_REGEX = re.compile(YTS)
