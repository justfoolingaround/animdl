"""
All the current providers that are made available in AnimDL.

The fetcher function must take session, url and check parameters to work.
"""

import re

from .animixplay import fetcher as animix_fetcher
from .twistmoe import fetcher as twist_fetcher
from .animepahe import fetcher as animepahe_fetcher
from .fouranime import fetcher as fouranime_fetcher

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
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?animepahe\.com/anime/([^?&/]+)"),
        'fetcher': animepahe_fetcher,
    },
    'fouranime': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?4anime\.to/(?:(?:anime/([^?&/]+))|(?:([^?&/]+)-episode-\d+))"),
        'fetcher': fouranime_fetcher,
    },
}

def get_provider(url):
    for provider, provider_data in current_providers.items():
        if provider_data.get('matcher').match(url):
            return provider_data
        
def get_appropriate(session, url, check=lambda *args: True):
    
    provider = get_provider(url)
    return provider.get('fetcher')(session, url, check)