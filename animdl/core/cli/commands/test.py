import logging

import click

from ...codebase import providers
from ..helpers import bannerify, ensure_extraction
from ..http_client import client


@click.command(name="test", help="Test the scrapability power.")
@click.option(
    "-x",
    help="A list of certain sites (full anime url) to be explicity used for testing.",
    default=[],
    required=False,
    multiple=True,
)
@click.option(
    "-e",
    help="Episode number to bestow the testing upon",
    default=1,
    required=False,
    type=int,
)
@click.option(
    "--log-file",
    help="Set a log file to log everything to.",
    required=False,
)
@click.option(
    "-ll", "--log-level", help="Set the integer log level.", type=int, default=20
)
@bannerify
def animdl_test(x, e, **kwargs):
    session = client
    SITE_LIST = {
        "9anime": "https://9anime.to/watch/one-piece.ov8",
        "crunchyroll": "https://www.crunchyroll.com/one-piece",
        "allanime": "https://allanime.site/anime/ReooPAxPMsHM4KPMY",
        "animeout": "https://www.animeout.xyz/download-one-piece-episodes-latest/",
        "animixplay": "https://animixplay.to/v1/one-piece",
        "animtime": "https://animtime.com/title/5",
        "gogoanime": "https://gogoanime.cm/category/one-piece",
        "tenshi": "https://tenshi.moe/anime/kjfrhu3s",
        "twist": "https://twist.moe/a/one-piece",
    }

    if not x:
        x = SITE_LIST.values()

    logger = logging.getLogger("tests")

    for site in x:
        logger.info("Attempting to scrape anime from {!r}.".format(site))
        try:
            links = [*providers.get_appropriate(session, site, lambda r: r == e)]
            if not links:
                raise Exception("No stream urls found on {!r}.".format(site))
            for link_cb, _ in links:
                for stream in ensure_extraction(session, link_cb):
                    print("\t - \x1b[32m{stream_url}\x1b[39m".format_map(stream))
            logger.info(
                "Scraping from {!r} was \x1b[32msuccessful\x1b[39m.".format(site)
            )
        except Exception as excep:
            logger.error(
                "\x1b[31mFailed to scrape any urls from {!r} due to {!r}.\x1b[39m".format(
                    site, excep
                )
            )
