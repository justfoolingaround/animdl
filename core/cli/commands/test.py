import click
import requests

from ...codebase import Associator
from ..helpers import to_stdout, bannerify

@click.command(name='test', help="Test the scrapability power.")
@click.option('-x', help='A list of certain sites (full anime url) to be explicity used for testing.', default=[], required=False, multiple=True)
@click.option('-e', help='Episode number to bestow the testing upon', default=1, required=False, type=int)
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@bannerify
def animdl_test(x, e, quiet):
    SITE_LIST = {
        '9anime': 'https://9anime.to/watch/one-piece.ov8',
        'anime1': 'https://www.anime1.com/watch/one-piece',
        'animepahe': requests.get('https://pahe.win/a/4', allow_redirects=False).headers.get('location', ''),
        'animeout': 'https://www.animeout.xyz/download-one-piece-episodes-latest/',
        'animixplay': 'https://animixplay.to/v1/one-piece',
        'gogoanime': 'https://gogoanime.ai/category/one-piece',
        'twist': 'https://twist.moe/a/one-piece',
    }

    if not x:
        x = SITE_LIST.values()
        
    ts = lambda x: to_stdout(x, caller='animdl-tests')
    
    for site in x:
        ts("Attempting to scrape anime from {!r}.".format(site))
        anime_associator = Associator(site)
        
        try:
            links = [*anime_associator.raw_fetch_using_check(lambda r: r == e)]
            if not links:
                raise Exception('No stream urls found on {!r}.'.format(site))            
            for link_cb, en in links:
                for stream in link_cb():
                    print('\t - \x1b[32m{stream_url}\x1b[39m'.format_map(stream))
            ts("Scraping from {!r} was \x1b[32msuccessful\x1b[39m.".format(site))
        except Exception as excep:
            ts("\x1b[31mFailed to scrape any urls from {!r} due to {!r}.\x1b[39m".format(site, excep))
