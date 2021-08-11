"""
All the current providers that are made available in AnimDL.

The fetcher function must take session, url and check parameters to work.
"""

from ...config import (ANIMEOUT, ANIMEPAHE, ANIMIXPLAY, ANIMTIME,
                       GOGOANIME, NINEANIME, TENSHI, TWIST)
from ..helper import construct_site_based_regex

from .animepahe import fetcher as animepahe_fetcher
from .animeout import fetcher as animeout_fetcher
from .animixplay import fetcher as animix_fetcher
from .animtime import fetcher as animtime_fetcher
from .gogoanime import fetcher as gogoanime_fetcher
from .nineanime import fetcher as nineanime_fetcher
from .tenshimoe import fetcher as tenshi_fetcher
from .twistmoe import fetcher as twist_fetcher

current_providers = {
    'animixplay': {
        'matcher': construct_site_based_regex(
            ANIMIXPLAY,
            extra_regex=r'/v\d+/([^?&/]+)'),
        'fetcher': animix_fetcher,
    },
    'twist': {
        'matcher': construct_site_based_regex(
            TWIST,
            extra_regex=r'/a/([^?&/]+)'),
        'fetcher': twist_fetcher,
    },
    'animepahe': {
        'matcher': construct_site_based_regex(
            ANIMEPAHE,
            extra_regex=r'/(?:anime|play)/([^?&/]+)'),
        'fetcher': animepahe_fetcher,
    },
    'gogoanime': {
        'matcher': construct_site_based_regex(
            GOGOANIME,
            extra_regex=r'/(?:([^&?/]+)-episode-\d+|category/([^&?/]+))'),
        'fetcher': gogoanime_fetcher,
    },
    '9anime': {
        'matcher': construct_site_based_regex(
            NINEANIME,
            extra_regex=r'/watch/[^&?/]+\.([^&?/]+)'),
        'fetcher': nineanime_fetcher,
    },
    'animeout': {
        'matcher': construct_site_based_regex(
            ANIMEOUT,
            extra_regex=r'/([^?&/]+)'),
        'fetcher': animeout_fetcher,
    },
    'tenshi': {
        'matcher': construct_site_based_regex(
            TENSHI,
            extra_regex=r'/anime/([^?&/]+)'),
        'fetcher': tenshi_fetcher,
    },
    'animtime': {
        'matcher': construct_site_based_regex(
            ANIMTIME,
            extra_regex=r'/title/([^?&/]+)'),
        'fetcher': animtime_fetcher,
    },
}


def get_provider(url):
    for provider, provider_data in current_providers.items():
        if provider_data.get('matcher').match(url):
            return provider, provider_data


def get_appropriate(session, url, check=lambda *args: True):
    provider_name, provider = get_provider(url)
    return provider.get('fetcher')(session, url, check)
