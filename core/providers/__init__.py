"""
All the current providers that are made available in AnimDL.

The fetcher function must take session, url and check parameters to work.
"""

import re

from .animixplay import fetcher as animix_fetcher
from .twistmoe import fetcher as twist_fetcher


current_providers = {
    'animix': {
        'matcher': re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v\d+/([^?&/]+)'),
        'fetcher': animix_fetcher,
        'download_headers': {}
    },
    'twistmoe': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?twist\.moe/a/([^?&/]+)"),
        'fetcher': twist_fetcher,
        'download_headers': {'referer': 'https://www.twist.moe/'}
    }
}

def get_provider(url):
    for provider, provider_data in current_providers.items():
        if provider_data.get('matcher').match(url):
            return provider_data
        
def get_appropriate(session, url, check=lambda *args: True):
    
    provider = get_provider(url)
    return provider.get('fetcher')(session, url, check), provider.get('download_headers')