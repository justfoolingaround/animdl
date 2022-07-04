import json
import logging

import click

from ...__version__ import __core__
from ...codebase import providers
from ...config import CHECK_FOR_UPDATES, DEFAULT_PROVIDER
from .. import helpers
from ..http_client import client


@click.command(
    name="grab", help="Stream the stream links to the stdout stream for external usage."
)
@helpers.decorators.content_fetch_options(
    include_quality_options=False,
    include_special_options=False,
)
@helpers.decorators.automatic_selection_options()
@helpers.decorators.logging_options()
@helpers.decorators.setup_loggers()
@helpers.decorators.banner_gift_wrapper(
    client, __core__, check_for_updates=CHECK_FOR_UPDATES
)
def animdl_grab(query, index, log_level, **kwargs):

    r = kwargs.get("range")

    logger = logging.getLogger("grabber")
    anime, provider = helpers.process_query(
        client, query, logger, auto_index=index, provider=DEFAULT_PROVIDER
    )

    if not anime:
        return

    logger.name = "{}/{}".format(provider, logger.name)
    logger.info("Initializing grabbing session.")

    for stream_url_caller, episode in providers.get_appropriate(
        client, anime.get("anime_url"), check=r
    ):
        stream_url = list(helpers.ensure_extraction(client, stream_url_caller))
        click.echo(json.dumps({"episode": episode, "streams": stream_url}))

    logger.info("Grabbing session complete.")
