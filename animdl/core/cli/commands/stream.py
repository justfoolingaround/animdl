import base64
import logging

import click
import yarl
from rich.errors import MarkupError
from rich.text import Text

from ...__version__ import __core__
from ...codebase import providers
from ...config import (
    CHECK_FOR_UPDATES,
    DEFAULT_PLAYER,
    DEFAULT_PROVIDER,
    DISCORD_PRESENCE,
    FORCE_STREAMING_QUALITY_SELECTION,
    QUALITY,
    USE_ANISKIP,
)
from .. import exit_codes, helpers, http_client

if DISCORD_PRESENCE:
    try:
        from ..helpers.rpc import set_streaming_episode
    except ImportError:
        raise ImportError(
            "Discord RPC was set to be enabled but `pypresence` is not installed, install it with `pip install pypresence`."
        )
    except RuntimeError:
        DISCORD_PRESENCE = False


@click.command(name="stream", help="Stream your favorite anime by query.")
@helpers.decorators.content_fetch_options(
    default_quality_string=QUALITY,
)
@helpers.decorators.player_options(default_player=DEFAULT_PLAYER)
@helpers.decorators.automatic_selection_options()
@helpers.decorators.logging_options()
@helpers.decorators.setup_loggers()
@helpers.decorators.banner_gift_wrapper(
    http_client.client, __core__, check_for_updates=CHECK_FOR_UPDATES
)
def animdl_stream(
    query, special, quality, player_opts, player, index, log_level, **kwargs
):
    """
    Streamer call for animdl streaming session.
    """
    r = kwargs.get("range")
    console = helpers.stream_handlers.get_console()

    logger = logging.getLogger("streamer")

    if player_opts is not None:
        player_opts = tuple(click.parser.split_arg_string(player_opts))
    else:
        player_opts = ()

    try:
        streamer = helpers.player.handle_player(DEFAULT_PLAYER, player_opts, player)
    except Exception:
        console.print_exception()
        raise SystemExit(exit_codes.STREAMER_CONFIGURATION_REQUIRED)

    anime, provider = helpers.process_query(
        http_client.client, query, console, auto_index=index, provider=DEFAULT_PROVIDER
    )

    if not anime:
        console.print(Text("Could not find an anime of that name :/."))
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

    with helpers.stream_handlers.context_raiser(
        console,
        Text(
            f"Scraping juicy streams from {provider!r}@{anime['anime_url']}",
            style="bold magenta",
        ),
        name="scraping",
    ):

        match, provider_module, _ = providers.get_provider(
            providers.append_protocol(anime.get("anime_url"))
        )

        streams = list(
            provider_module.fetcher(
                http_client.client, anime.get("anime_url"), r, match
            )
        )

        if special:
            streams = list(helpers.special.special_parser(streams, special))

        content_title = anime["name"]

        total = len(streams)

        if total < 1:
            console.print(Text("Could not find any streams on the site :/."))
            console.print(
                "This could mean that, either those episodes are unavailable or that the scraper has broke.",
                style="dim",
            )
            return exit(exit_codes.NO_CONTENT_FOUND)

        with helpers.stream_handlers.context_raiser(
            console, f"Now streaming {content_title!r}", name="streaming"
        ):

            for count, (stream_urls_caller, episode_number) in enumerate(streams, 1):

                if episode_number == 0:
                    episode_text = "Special Episode"
                else:
                    episode_text = f"Episode {episode_number}"

                if content_title:
                    media_title = f"{content_title}: {episode_text}"
                else:
                    media_title = episode_text

                playing = True

                while playing:

                    stream_urls = list(
                        helpers.ensure_extraction(
                            http_client.client, stream_urls_caller
                        )
                    )

                    if not stream_urls:

                        console.print(
                            Text(
                                f"Could not find any streams for {episode_text!r} :/."
                            ),
                            Text(
                                "Loading in DEBUG [--log-level=0] mode allows extraction retrial.",
                                style="dim",
                            ),
                        )

                        if log_level <= logging.DEBUG:
                            playing = click.confirm("Retry stream url extraction?")

                        continue

                    titles = set(_.get("title") for _ in stream_urls)

                    if len(titles) > 1 and FORCE_STREAMING_QUALITY_SELECTION:
                        console.print(
                            Text(
                                f"Multiple titles found for the same streams, multiple seasons may be available. Please adjust the quality string as required: {', '.join(map(repr, titles))}",
                                style="dim",
                            ),
                        )

                    selection = helpers.prompts.quality_prompt(
                        console,
                        stream_urls,
                        force_selection_string=quality
                        if FORCE_STREAMING_QUALITY_SELECTION
                        else None,
                    )

                    headers = selection.get("headers", {})

                    logger.debug(f"Obtained streams: {stream_urls!r}")

                    if "title" in selection:
                        media_title += f" ({selection['title']})"

                    if USE_ANISKIP:
                        chapters = helpers.aniskip.get_timestamps(
                            http_client.client, content_title, episode_number
                        )
                    else:
                        chapters = []

                    with helpers.stream_handlers.context_raiser(
                        console,
                        f"Currently playing: {episode_text!r}. [dim]{total-count:d} episodes in queue.[/]",
                        name="playing",
                    ):
                        if not headers:
                            shareable_url = yarl.URL(
                                "https://plyr.link/p/player.html"
                            ).with_fragment(
                                base64.b64encode(
                                    selection["stream_url"].encode()
                                ).decode()
                            )
                            console.print(
                                Text(
                                    f"This stream may be share-able [embeddable and playable as a single URL] (please note that subtitles, chapters and titles won't be embedded)."
                                ),
                                style="dim",
                            )

                            try:
                                console.print(
                                    f"[dim]Share-ables: [link={shareable_url}]embed[/link], [link={selection['stream_url']}]direct url[/link][/dim]"
                                )
                            except MarkupError:
                                pass

                        with streamer:
                            streamer.play(
                                selection["stream_url"],
                                title=media_title,
                                headers=headers,
                                subtitles=selection.get("subtitle", []),
                                chapters=chapters,
                            )

                            if DISCORD_PRESENCE:
                                set_streaming_episode(
                                    http_client.client, content_title, episode_number
                                )

                    error_indication = streamer.indicate_error()

                    if bool(error_indication):
                        logger.warning(
                            f"Streamer indicated an error {error_indication!r}."
                        )

                        if log_level <= logging.INFO:
                            if click.confirm("Retry streaming this episode?"):
                                continue

                    if log_level <= logging.DEBUG:
                        if click.confirm("Replay episode?"):
                            continue

                    playing = False
