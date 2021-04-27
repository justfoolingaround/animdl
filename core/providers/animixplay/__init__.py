from .stream_url import *
from .search import *

AVAILABLE_PARSERS = {
    'gogo-anime': {
        'matcher': re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v1/([^?&/]+)'),
        'parser': lambda session, url, check=lambda *args: True: fetching_chain(from_site_url, gogoanime_parser, session, url, check),
    }
}

def get_parser(url):
    for parser, data in AVAILABLE_PARSERS.items():
        if data.get('matcher').match(url):
            return data.get('parser')
        
fetcher = lambda session, url, check=lambda *args: True: get_parser(url)(session, url, check=check)