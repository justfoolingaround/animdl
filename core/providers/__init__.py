"""
All the current providers that are made available in AnimDL.

The fetcher function must take session, url and check parameters to work.
"""

import re

from .animefreak import fetcher as animefreak_fetcher
from .animepahe  import fetcher as animepahe_fetcher
from .animixplay import fetcher as animix_fetcher
from .fouranime  import fetcher as fouranime_fetcher
from .gogoanime  import fetcher as gogoanime_fetcher
from .nineanime  import fetcher as nineanime_fetcher
from .twistmoe   import fetcher as twist_fetcher

current_providers = {
    'animix': {
        'matcher': re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v\d+/([^?&/]+)'),
        'fetcher': animix_fetcher,
    },
    'twistmoe': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?twist\.moe/a/([^?&/]+)"),
        'fetcher': twist_fetcher,
    },
    'animepahe': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?animepahe\.com/(?:anime|play)/([^?&/]+)"),
        'fetcher': animepahe_fetcher,
    },
    'fouranime': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?4anime\.to/(?:(?:anime/([^?&/]+))|(?:([^?&/]+)-episode-\d+))"),
        'fetcher': fouranime_fetcher,
    },
    'gogoanime': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?gogoanime\.ai/(?:([^&?/]+)-episode-\d+|category/([^&?/]+))"),
        'fetcher': gogoanime_fetcher,
    },
    '9anime': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?9anime\.to/watch/[^&?/]+\.([^&?/]+)"),
        'fetcher': nineanime_fetcher,
    },
    'animefreak': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?animefreak\.tv/watch/(?:(?:([^?&/]+)/episode/episode-\d+)|(?:([^?&/]+)))"),
        'fetcher': animefreak_fetcher,
    }
}

def get_provider(url):
    for provider, provider_data in current_providers.items():
        if provider_data.get('matcher').match(url):
            return provider, provider_data


def get_appropriate(session, url, check=lambda *args: True):
    provider_name, provider = get_provider(url)
    return provider.get('fetcher')(session, url, check)
