import logging

import click
import httpx

from ...codebase import Associator
from ..helpers import bannerify, to_stdout


@click.command(name='test', help="Test the scrapability power.")
@click.option('-x',
              help='A list of certain sites (full anime url) to be explicity used for testing.',
              default=[],
              required=False,
              multiple=True)
@click.option('-e',
              help='Episode number to bestow the testing upon',
              default=1,
              required=False,
              type=int)
@click.option('-ll',
              '--log-level',
              help='Set the integer log level.',
              type=int,
              default=20)
@bannerify
def animdl_test(x, e, log_level):
    session = httpx.Client()
    SITE_LIST = {
        '9anime': 'https://9anime.to/watch/one-piece.ov8',
        'animepahe': session.get(
            'https://pahe.win/a/4',
            allow_redirects=False).headers.get(
            'location',
            ''),
        'animeout': 'https://www.animeout.xyz/download-one-piece-episodes-latest/',
        'animixplay': 'https://animixplay.to/v1/one-piece',
        'animtime': 'https://animtime.com/title/5',
        'gogoanime': 'https://gogoanime.pe/category/one-piece',
        'tenshi': 'https://tenshi.moe/anime/kjfrhu3s',
        'twist': 'https://twist.moe/a/one-piece',
    }

    if not x:
        x = SITE_LIST.values()

    logger = logging.getLogger('animdl-tests')

    for site in x:
        logger.info("Attempting to scrape anime from {!r}.".format(site))
        anime_associator = Associator(site, session=session)

        try:
            links = [*anime_associator.raw_fetch_using_check(lambda r: r == e)]
            if not links:
                raise Exception('No stream urls found on {!r}.'.format(site))
            for link_cb, en in links:
                for stream in link_cb():
                    print(
                        '\t - \x1b[32m{stream_url}\x1b[39m'.format_map(stream))
            logger.info(
                "Scraping from {!r} was \x1b[32msuccessful\x1b[39m.".format(site))
        except Exception as excep:
            logger.error(
                "\x1b[31mFailed to scrape any urls from {!r} due to {!r}.\x1b[39m".format(
                    site, excep))
