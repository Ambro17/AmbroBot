import re

# Regexps to match hashtags the snippet to be saved.
# Accepts A-Za-z0-9, underscore, hyphen and closing question mark
SAVE_REGEX = re.compile(r'^#(?P<key>[\w\-?]+) +(?P<content>[\s\S]+)')
GET_REGEX = re.compile(r'^@get (?P<key>[\w\-?]+)')
DELETE_REGEX = re.compile(r'^@delete (?P<key>[\w\-?]+)')
