import logging
from collections import defaultdict

import click

from ...codebase import providers
from ...config import DEFAULT_PLAYER, QUALITY
from .. import exit_codes, helpers, http_client
from ..helpers.intelliq import filter_quality


def quality_prompt(log_level, logger, stream_list):
    title_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for n, anime in enumerate(stream_list, 1):
        title_dict[anime.get("title") or "Uncategorized"][
            anime.get("quality") or "No specific quality mentioned"
        ][
            "Soft subtitles (Subtitles are not forced.)"
            if anime.get("subtitle")
            else "Hard subtitles (Subtitles are forced.)"
        ].append(
            "{:02d}: {}".format(n, helpers.stream_judiciary(anime.get("stream_url")))
        )

    for category, qualities in title_dict.items():
        logger.info("\x1b[91m▽ {}\x1b[39m".format(category))
        for quality, subtitles in qualities.items():
            logger.info("\x1b[96m▽▽ {}\x1b[39m".format(quality))
            for subtitle, animes in subtitles.items():
                logger.info("\x1b[95m▽▽▽ {}\x1b[39m".format(subtitle))
                for anime in animes:
                    logger.info(anime)

    return stream_list[
        (
            helpers.ask(
                log_level,
                text="Select above, using the stream index",
                show_default=True,
                default=1,
                type=int,
            )
            - 1
        )
        % len(stream_list)
    ]


@click.command(name="stream", help="Stream your favorite anime by query.")
@click.argument("query", required=True)
@click.option(
    "-r",
    "--range",
    help="Select ranges of anime.",
    required=False,
    default=":",
    type=str,
)
@click.option(
    "--player-opts",
    help="Arguments that are to be passed to the player call.",
    required=False,
)
@click.option(
    "-q",
    "--quality",
    help="Use quality strings.",
    required=False,
    default=QUALITY,
)
@click.option(
    "-p",
    "--player",
    help="Select which player to play from.",
    required=False,
    default=DEFAULT_PLAYER,
    show_default=True,
    show_choices=True,
    type=click.Choice(
        ("mpv", "vlc", "iina", "celluloid", "ffplay", "android"), case_sensitive=False
    ),
)
@click.option(
    "--auto",
    is_flag=True,
    default=False,
    help="Select the first given index without asking for prompts.",
)
@click.option(
    "-i",
    "--index",
    required=False,
    default=0,
    show_default=False,
    type=int,
    help="Index for the auto flag.",
)
@click.option(
    "--log-file",
    help="Set a log file to log everything to.",
    required=False,
)
@click.option(
    "-ll", "--log-level", help="Set the integer log level.", type=int, default=20
)
@helpers.bannerify
def animdl_stream(
    query, player_opts, quality, player, auto, index, log_level, **kwargs
):
    """
    Streamer call for animdl streaming session.
    """
    r = kwargs.get("range")

    session = http_client.client
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
        session, query, logger, auto=auto, auto_index=index
    )

    if not anime:
        logger.critical("Searcher returned no anime to stream, failed to stream.")
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

    logger.name = "{}/{}".format(provider, logger.name)
    logger.debug("Will scrape from {}".format(anime))
    logger.info("Now initiating your stream session")

    enqueuer = providers.get_appropriate(
        session, anime.get("anime_url"), helpers.get_check(r)
    )

    streams = list(enqueuer)
    total = len(streams)

    for count, (stream_urls_caller, episode_number) in enumerate(streams, 1):

        playing = True
        while playing:

            window_title = "Episode {:02d}".format(int(episode_number))

            stream_urls = filter_quality(
                list(helpers.ensure_extraction(session, stream_urls_caller)), quality
            )

            if not stream_urls:
                logger.warning(
                    "There were no stream links available at the moment. Ignoring {!r}, retry using a different provider.".format(
                        window_title
                    )
                )
                playing = False
                continue

            selection = (
                quality_prompt(log_level, logger, stream_urls)
                if len(stream_urls) > 1
                else stream_urls[0]
            )

            if selection.pop("is_torrent", False):
                logging.warning(
                    "Obtained torrent in streaming, please download the torrent and stream it. (Torrent downloads take place in sequential order.)"
                )
                continue

            logger.debug("Calling streamer for {!r}".format(stream_urls))

            headers = selection.get("headers", {})
            _ = headers.pop("ssl_verification", True)

            logger.info(
                "Streaming {!r}, [{:d}/{:d}, {:d} remaining]".format(
                    window_title, count, total, total - count
                )
            )

            player_process = streamer(
                selection.get("stream_url"),
                headers=headers,
                content_title=selection.get("title") or window_title,
                subtitles=selection.get("subtitle", []),
            )
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
