import json as json_

import click
import requests

from ...config import DEFAULT_PROVIDER
from ..helpers import bannerify, to_stdout
from ..helpers.searcher import link

@click.command(name='search', help="Search for an anime in the provider.")
@click.argument('query', required=True)
@click.option('-p', '--provider', help='Provider to search in.', required=False, default=DEFAULT_PROVIDER)
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@click.option('-j', '--json', help="An integer that determines where to begin the grabbing from.", is_flag=True, flag_value=True)
@bannerify
def animdl_search(query, json, provider, quiet):
    
    announcer = lambda x: to_stdout(x, 'animdl-searcher') if not quiet else None
    session = requests.Session()

    if not provider in link:
        announcer("{!r} is not supported at the moment. Selecting the default {!r}.".format(provider, DEFAULT_PROVIDER))
        provider = DEFAULT_PROVIDER

    for i, search_data in enumerate(link.get(provider)(session, query)):
        to_stdout(json_.dumps(search_data) if json else '[#{:02d}] {name} \x1b[33m{anime_url}\x1b[39m'.format(i, **search_data), '')