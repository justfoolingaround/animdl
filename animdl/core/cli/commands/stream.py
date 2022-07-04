import logging

import click

from ...__version__ import __core__
from ...codebase import providers
from ...config import (
    CHECK_FOR_UPDATES,
    DEFAULT_PLAYER,
    DEFAULT_PROVIDER,
    DISCORD_PRESENCE,
    FORCE_STREAMING_QUALITY_SELECTION,
    QUALITY,
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

    logger = logging.getLogger("streamer")
    streamer = helpers.handle_streamer(
        click.parser.split_arg_string(player_opts or "") or [], **{player: True}
    )

    if streamer is False:
        logger.critical(
            "Streaming failed due to selection of a unsupported streamer; please configure the streamer in the config to use it."
        )
        raise SystemExit(exit_codes.STREAMER_CONFIGURATION_REQUIRED)

    anime, provider = helpers.process_query(
        http_client.client, query, logger, auto_index=index, provider=DEFAULT_PROVIDER
    )

    if not anime:
        logger.critical("Searcher returned no anime to stream, failed to stream.")
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

    logger.name = "{}/{}".format(provider, logger.name)
    logger.debug("Will scrape from {}".format(anime))
    logger.info("Now initiating your stream session")

    match, provider_module, _ = providers.get_provider(
        providers.append_protocol(anime.get("anime_url"))
    )

    streams = list(
        provider_module.fetcher(http_client.client, anime.get("anime_url"), r, match)
    )

    if special:
        streams = list(helpers.special.special_parser(streams, special))

    content_title = anime["name"]

    total = len(streams)
    for count, (stream_urls_caller, episode_number) in enumerate(streams, 1):

        playing = True
        while playing:

            window_title = content_title + ": Episode {}".format(episode_number)

            stream_urls = list(
                helpers.ensure_extraction(http_client.client, stream_urls_caller)
            )

            if not stream_urls:
                logger.warning(
                    "There were no stream links available at the moment. Ignoring {!r}, retry using a different provider.".format(
                        window_title
                    )
                )
                playing = False
                continue

            selection = helpers.prompts.quality_prompt(
                logger,
                log_level,
                stream_urls,
                force_selection_string=quality
                if FORCE_STREAMING_QUALITY_SELECTION
                else None,
            )

            logger.debug("Calling streamer for {!r}".format(stream_urls))

            headers = selection.get("headers", {})
            _ = headers.pop("ssl_verification", True)

            logger.info(
                "Streaming {!r}, [{:d}/{:d}, {:d} remaining]".format(
                    window_title, count, total, total - count
                )
            )

            if "title" in selection:
                window_title += " ({})".format(selection["title"])

            player_process = streamer(
                selection.get("stream_url"),
                headers=headers,
                content_title=window_title,
                subtitles=selection.get("subtitle", []),
            )
            if DISCORD_PRESENCE:
                set_streaming_episode(http_client.client, content_title, episode_number)

            player_process.wait()

            if player_process.returncode:
                logger.warning(
                    "Detected a non-zero return code: {:d}.".format(
                        player_process.returncode
                    )
                )
                playing = (
                    False
                    if log_level > 20
                    else click.confirm(
                        "Retry playback for {!r}?".format(window_title),
                        show_default=True,
                        default=False,
                    )
                )
                continue

            playing = (
                False
                if log_level > 10
                else click.confirm(
                    "Replay {!r}?".format(window_title), show_default=True, default=True
                )
            )
