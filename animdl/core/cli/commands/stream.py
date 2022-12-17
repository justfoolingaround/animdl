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

    logger = logging.getLogger("streamer")

    if player_opts is not None:
        player_opts = tuple(click.parser.split_arg_string(player_opts))
    else:
        player_opts = ()

    try:
        streamer = helpers.player.handle_player(DEFAULT_PLAYER, player_opts, player)
    except Exception as e:
        logger.error(
            "Streaming failed due to: {!r}.".format(e),
            exc_info=True,
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

    if total < 1:
        logger.critical("No streams found, failed to stream.")
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

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
                helpers.ensure_extraction(http_client.client, stream_urls_caller)
            )

            if not stream_urls:

                logger.warning(
                    f"Could not find stream urls for {content_title!r}. "
                    "The episode may not be available or the scraper has broke."
                )

                if log_level <= logging.DEBUG:
                    playing = click.confirm("Retry stream url extraction?")

                continue

            selection = helpers.prompts.quality_prompt(
                logger,
                log_level,
                stream_urls,
                force_selection_string=quality
                if FORCE_STREAMING_QUALITY_SELECTION
                else None,
            )

            headers = selection.get("headers", {})

            logger.info(
                f"Streaming {media_title!r}, [{count:d}/{total:d}, {total - count:d} remaining]"
            )
            logger.debug(f"Obtained streams: {stream_urls!r}")

            if "title" in selection:
                media_title += " ({})".format(selection["title"])

            if USE_ANISKIP:
                chapters = helpers.aniskip.get_timestamps(
                    http_client.client, content_title, episode_number
                )
            else:
                chapters = []

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
                logger.warning(f"Streamer indicated an error {error_indication!r}.")

                if log_level <= logging.INFO:
                    if click.confirm("Retry streaming this episode?"):
                        continue

            if log_level <= logging.DEBUG:
                if click.confirm("Replay episode?"):
                    continue

            playing = False
