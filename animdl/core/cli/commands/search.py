import json as json_
import logging

import click

from ...config import DEFAULT_PROVIDER
from ..helpers import bannerify
from ..helpers.searcher import link
from ..http_client import client


@click.command(name="search", help="Search for an anime in the provider.")
@click.argument("query", required=True)
@click.option(
    "-p",
    "--provider",
    help="Provider to search in.",
    required=False,
    default=DEFAULT_PROVIDER,
)
@click.option(
    "-ll", "--log-level", help="Set the integer log level.", type=int, default=20
)
@click.option(
    "--log-file",
    help="Set a log file to log everything to.",
    required=False,
)
@click.option(
    "-j",
    "--json",
    help="An integer that determines where to begin the grabbing from.",
    is_flag=True,
    flag_value=True,
)
@bannerify
def animdl_search(query, json, provider, **kwargs):
    logger = logging.getLogger("searcher")
    session = client

    if provider not in link:
        logger.critical(
            "{!r} is not supported at the moment. Selecting the default {!r}.".format(
                provider, DEFAULT_PROVIDER
            )
        )
        provider = DEFAULT_PROVIDER

    genexp = link.get(provider)(session, query)

    for i, search_data in enumerate(genexp):
        logger.info(
            "[#{:02d}] {name} \x1b[33m{anime_url}\x1b[39m".format(i, **search_data)
        ) if not json else print(json_.dumps(search_data))
