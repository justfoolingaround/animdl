from .stream_url import *
from .search import *

from ....config import ANIMIXPLAY
from ...helper import construct_site_based_regex

AVAILABLE_PARSERS = {
    'gogo-anime': {
        'matcher': construct_site_based_regex(ANIMIXPLAY, extra_regex=r"/v1/([^?&/]+)"),
        'parser': lambda session, url, check=lambda *args: True: fetching_chain(from_site_url, gogoanime_parser, session, url, check),
    }
}

def get_parser(url):
    for parser, data in AVAILABLE_PARSERS.items():
        if data.get('matcher').match(url):
            return data.get('parser')
        
fetcher = lambda session, url, check=lambda *args: True: get_parser(url)(session, url, check=check)