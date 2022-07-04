import json as json_
import logging

import click

from ...__version__ import __core__
from ...codebase.providers import get_provider
from ...config import CHECK_FOR_UPDATES, DEFAULT_PROVIDER
from .. import helpers
from ..http_client import client


@click.command(name="search", help="Search for an anime in the provider.")
@click.argument("query", required=True)
@click.option(
    "-p",
    "--provider",
    help="Provider to search in.",
    default=DEFAULT_PROVIDER,
    type=click.Choice(helpers.provider_searcher_mapping.keys(), case_sensitive=False),
)
@helpers.decorators.logging_options()
@click.option(
    "-j",
    "--json",
    help="Output as json.",
    is_flag=True,
    flag_value=True,
)
@helpers.decorators.setup_loggers()
@helpers.decorators.banner_gift_wrapper(
    client, __core__, check_for_updates=CHECK_FOR_UPDATES
)
def animdl_search(query, json, provider, **kwargs):
    logger = logging.getLogger("searcher")

    match, module, _ = get_provider(query, raise_on_failure=False)

    if module is not None:
        genexp = (
            {
                "name": (
                    module.metadata_fetcher(client, query, match)["titles"] or [None]
                )[0]
                or "",
                "anime_url": query,
            },
        )
    else:
        genexp = helpers.provider_searcher_mapping.get(provider)(client, query)

    for count, search_data in enumerate(genexp, 1):
        if json:
            print(json_.dumps(search_data))
        else:
            logger.info("{0:02d}: {1[name]} {1[anime_url]}".format(count, search_data))
