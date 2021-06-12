"""
All the current providers that are made available in AnimDL.

The fetcher function must take session, url and check parameters to work.
"""

from .anime1     import fetcher as anime1_fetcher
from .animefreak import fetcher as animefreak_fetcher
from .animepahe  import fetcher as animepahe_fetcher
from .animixplay import fetcher as animix_fetcher
from .fouranime  import fetcher as fouranime_fetcher
from .gogoanime  import fetcher as gogoanime_fetcher
from .nineanime  import fetcher as nineanime_fetcher
from .twistmoe   import fetcher as twist_fetcher

from ..helper import construct_site_based_regex
from ..config import *

current_providers = {
    'animixplay': {
        'matcher': construct_site_based_regex(ANIMIXPLAY, extra_regex=r'/v\d+/([^?&/]+)'),
        'fetcher': animix_fetcher,
    },
    'twist': {
        'matcher': construct_site_based_regex(TWIST, extra_regex=r'/a/([^?&/]+)'),
        'fetcher': twist_fetcher,
    },
    'animepahe': {
        'matcher': construct_site_based_regex(ANIMEPAHE, extra_regex=r'/(?:anime|play)/([^?&/]+)'),
        'fetcher': animepahe_fetcher,
    },
    '4anime': {
        'matcher': construct_site_based_regex(FOURANIME, extra_regex=r'/(?:(?:anime/([^?&/]+))|(?:([^?&/]+)-episode-\d+))'),
        'fetcher': fouranime_fetcher,
    },
    'gogoanime': {
        'matcher': construct_site_based_regex(GOGOANIME, extra_regex=r'/(?:([^&?/]+)-episode-\d+|category/([^&?/]+))'),
        'fetcher': gogoanime_fetcher,
    },
    '9anime': {
        'matcher': construct_site_based_regex(NINEANIME, extra_regex=r'/watch/[^&?/]+\.([^&?/]+)'),
        'fetcher': nineanime_fetcher,
    },
    'animefreak': {
        'matcher': construct_site_based_regex(ANIMEFREAK, extra_regex=r'/watch/(?:(?:([^?&/]+)/episode/episode-\d+)|(?:([^?&/]+)))'),
        'fetcher': animefreak_fetcher,
    },
    'anime1': {
        'matcher': construct_site_based_regex(ANIME1, extra_regex=r'/watch/([^?&/]+)'),
        'fetcher': anime1_fetcher,
    }
}

def get_provider(url):
    for provider, provider_data in current_providers.items():
        if provider_data.get('matcher').match(url):
            return provider, provider_data


def get_appropriate(session, url, check=lambda *args: True):
    provider_name, provider = get_provider(url)
    return provider.get('fetcher')(session, url, check)
