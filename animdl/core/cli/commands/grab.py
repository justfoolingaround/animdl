import json

import click

from ...__version__ import __core__
from ...codebase import providers
from ...config import CHECK_FOR_UPDATES, DEFAULT_PROVIDER
from .. import helpers
from ..http_client import client


@click.command(
    name="grab", help="Stream the stream links to the stdout stream for external usage."
)
@click.option(
    "--anime-url",
    "-u",
    type=str,
    default=None,
    help="Use the URL for a specific anime, overrides query."
)
@click.option(
    "--episode-list",
    "-e",
    type=bool,
    default=False,
    help="Only return a list of episode numbers for the given anime.",
    is_flag=True
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
def animdl_grab(query, index, **kwargs):

    console = helpers.stream_handlers.get_console()
    console.print(
        "The content is outputted to [green]stdout[/] while these messages are outputted to [red]stderr[/]."
    )

    anime_url = kwargs.get("anime_url")
    if anime_url is None:
        anime, provider = helpers.process_query(
            client, query, console, auto_index=index, provider=DEFAULT_PROVIDER
        )
        if not anime:
            return
        anime_url = anime.get("anime_url")

    if kwargs.get("episode_list"):
        episodes = []
        for _, episode in providers.get_appropriate(
            client, anime_url, check=kwargs.get("range")
        ):
            episodes.append(episode)
        click.echo(json.dumps({"episodes": episodes}))
        return

    for stream_url_caller, episode in providers.get_appropriate(
        client, anime_url, check=kwargs.get("range")
    ):
        stream_url = list(helpers.ensure_extraction(client, stream_url_caller))
        click.echo(json.dumps({"episode": episode, "streams": stream_url}))
