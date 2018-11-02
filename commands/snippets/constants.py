import re

# Regexps to match hashtags the snippet to be saved.
# Accepts A-Za-z0-9, underscore, hyphen and closing question mark
SAVE_REGEX = re.compile(r'^#(?P<key>[\w\-?]+) +(?P<content>[\s\S]+)')
GET_REGEX = re.compile(r'^@get (?P<key>[\w\-?]+)')
DELETE_REGEX = re.compile(r'^@delete (?P<key>[\w\-?]+)')

DEFAULT_ERROR_MESSAGE = (
    'Algo salió mal y no pude guardar tu snippet.\n'
    'Podés intentar más tarde o aceptar que en el mundo reina el caos.'
)

DUPLICATE_KEY_MESSAGE = (
    '⛔️ La clave `{}` ya existe en la base de datos.\n'
    'Elegí otra para guardar tu snippet 🙏'
)
