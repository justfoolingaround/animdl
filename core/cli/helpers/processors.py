"""
Query processors for AnimDL's cli.
"""

import re

from click.termui import prompt

from ...codebase.providers import current_providers as URL_MATCHERS
from ...config import DEFAULT_PROVIDER
from .fun import to_stdout
from .searcher import get_searcher

INCLUDED_PROVIDER = re.compile(r"^(?P<provider>.*):(?P<query>.*)", re.S)

def prompt_user(anime_list_genexp, provider_name):
    ts = lambda x: to_stdout(x, "animdl-%s-searcher" % provider_name)        
    r = []
    for n, anime in enumerate(anime_list_genexp, 1):
        ts("[#{:02d}] {} \x1b[33m{}\x1b[39m".format(n, anime.get('name'), anime.get('anime_url')))
        r.append(anime)
    
    if not r:
        print("[\x1b[31manimdl-{}-{}\x1b[39m] {}".format(provider_name, 'searcher', 'Cannot find anything of that query.'))
        return {}, None
    
    index = prompt("Select by the index (defaults to 1)", default=1, type=int, show_default=False) - 1
    if (index + 1) > len(r):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(r) + 1))
        index %= len(r)
    
    return r[index], provider_name
    
def process_query(session, query, *, provider=DEFAULT_PROVIDER):
    
    for url, matcher_data in URL_MATCHERS.items():
        if matcher_data.get('matcher').search(query):
            return {'anime_url': query}, url
    
    query_match = INCLUDED_PROVIDER.search(query)
    if query_match:
        query, provider = query_match.group('query', 'provider')
        provider = provider.lower()
    
    if not provider.lower() in URL_MATCHERS:
        query = "%s:%s" % (provider, query)
        provider = DEFAULT_PROVIDER
    
    return prompt_user(get_searcher(provider)(session, query), provider)
