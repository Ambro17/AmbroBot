import re

IMDB_LINK = 'https://www.imdb.com/title/{}'
IMDB_TT_LINK = 'https://www.imdb.com/title/tt{}'
YT_LINK = 'https://www.youtube.com/watch?v={}'

COMANDO_DESCONOCIDO = [
    'No sé qué decirte..',
    'Sabes que no te entiendo..',
    'Todavía no aprendí ese comando',
    'Mmmm no entiendo',
    'No sé cómo interpretar tu pedido',
    'No respondo a ese comando',
    'No conozco a ese comando. Lo escribiste bien?',
    'No entiendo qué querés.',
    'No existe ese comando.',
]

# Ticket ids of 5 or 6 numbers preceded by t|osp||osp- or any casing variant.
TICKET_REGEX = re.compile(r'(t|osp-?)(?P<ticket>\d{5,6})', re.IGNORECASE)


# Text starting with ~, \c, \code or $ will be monospaced formatted
CODE_PREFIX = re.compile(r'^(~|\\code|\$|\\c) (?P<code>[\s\S]+)')

# Minute in seconds
MINUTE = 60

# Buenos aires GMT offset
GMT_BUENOS_AIRES = -3