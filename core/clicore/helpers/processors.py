"""
Query processors for AnimDL's cli.
"""

import re

from click.termui import prompt

from .fun import to_stdout
from .searchonsite import get_searcher

DEFAULT_SITE = "9anime" # Forced-default to choose from.

URL_MATCHERS = {
    'animixplay': {
        'matcher': re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v\d+/([^?&/]+)'),
    },
    'twist': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?twist\.moe/a/([^?&/]+)"),
    },
    'animepahe': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?animepahe\.com/(?:anime|play)/([^?&/]+)"),
    },
    '4anime': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?4anime\.to/(?:(?:anime/([^?&/]+))|(?:([^?&/]+)-episode-\d+))"),
    },
    'gogoanime': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?gogoanime\.ai/(?:([^&?/]+)-episode-\d+|category/([^&?/]+))"),
    },
    '9anime': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?9anime\.to/watch/[^&?/]+\.([^&?/]+)"),
    },
    'animefreak': {
        'matcher': re.compile(r"^(?:https?://)?(?:\S+\.)?animefreak\.tv/watch/(?:(?:([^?&/]+)/episode/episode-\d+)|(?:([^?&/]+)))"),
    }
}

INCLUDED_PROVIDER = re.compile(r"^(?P<provider>.*):(?P<query>.*)", re.S)

def prompt_user(anime_list, provider_name):
    ts = lambda x: to_stdout(x, "%s-searcher" % provider_name)
    ts("Found %d anime(s)" % len(anime_list))
    for n, anime in enumerate(anime_list, 1):
        ts("[#%02d] %s" % (n, anime.get('name')))
    
    index = prompt("Select by the index (defaults to 1)", default=1, type=int, show_default=False) - 1
    
    if (index + 1) > len(anime_list):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(anime_list) + 1))
        index %= len(anime_list)
    
    return anime_list[index], provider_name
    
def process_query(session, query, *, provider=DEFAULT_SITE):
    
    for url, matcher_data in URL_MATCHERS.items():
        if matcher_data.get('matcher').search(query):
            return {'anime_url': query}, url
    
    query_match = INCLUDED_PROVIDER.search(query)
    if query_match:
        query, provider = query_match.group('query', 'provider')
        provider = provider.lower()
    
    if not provider.lower() in URL_MATCHERS:
        query = "%s:%s" % (provider, query)
        provider = DEFAULT_SITE
    
    return prompt_user([*get_searcher(provider)(session, query)], provider)
