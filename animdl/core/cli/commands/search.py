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
    default=DEFAULT_PROVIDER,
    type=click.Choice(link.keys(), case_sensitive=False),
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
    help="Output as json.",
    is_flag=True,
    flag_value=True,
)
@bannerify
def animdl_search(query, json, provider, **kwargs):
    logger = logging.getLogger("searcher")
    genexp = link.get(provider)(client, query)

    for count, search_data in enumerate(genexp, 1):
        if json:
            print(json_.dumps(search_data))
        else:
            logger.info("{0:02d}: {1[name]} {1[anime_url]}".format(count, search_data))
