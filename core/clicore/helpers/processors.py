"""
Query processors for AnimDL's cli.
"""

import re

from click.termui import prompt

from .fun import to_stdout
from .searchonsite import get_searcher

from ...providers import current_providers as URL_MATCHERS

DEFAULT_SITE = "9anime" # Forced-default to choose from.

INCLUDED_PROVIDER = re.compile(r"^(?P<provider>.*):(?P<query>.*)", re.S)

def prompt_user(anime_list_genexp, provider_name):
    ts = lambda x: to_stdout(x, "%s-searcher" % provider_name)        
    r = []
    for n, anime in enumerate(anime_list_genexp, 1):
        ts("[#%02d] %s \x1b[33m%s\x1b[39m" % (n, anime.get('name'), anime.get('anime_url')))
        r.append(anime)
    
    index = prompt("Select by the index (defaults to 1)", default=1, type=int, show_default=False) - 1
    if (index + 1) > len(r):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(r) + 1))
        index %= len(r)
    
    return r[index], provider_name
    
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
    
    return prompt_user(get_searcher(provider)(session, query), provider)