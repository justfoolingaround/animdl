import logging
from pathlib import Path

import click

from ...codebase import providers, sanitize_filename
from ...config import AUTO_RETRY, QUALITY
from .. import exit_codes, helpers, http_client


@click.command(name="download", help="Download your favorite anime by query.")
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
    "-s",
    "--special",
    help="Special range selection.",
    required=False,
    default="",
    type=str,
)
@click.option(
    "-q",
    "--quality",
    help="Use quality strings.",
    required=False,
    default=QUALITY,
)
@click.option(
    "-d",
    "--download-folder",
    help="Download folder name for the anime.",
    required=False,
    default="",
    show_default=False,
)
@click.option(
    "--idm",
    is_flag=True,
    default=False,
    help="Download anime using Internet Download Manager",
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
    default=1,
    show_default=False,
    type=int,
    help="Index for the auto flag.",
)
@click.option("--log-file", help="Set a log file to log everything to.", required=False)
@click.option(
    "-ll", "--log-level", help="Set the integer log level.", type=int, default=20
)
@helpers.bannerify
def animdl_download(
    query, special, quality, download_folder, idm, auto, index, log_level, **kwargs
):

    r = kwargs.get("range")

    session = http_client.client
    logger = logging.getLogger("downloader")

    anime, provider = helpers.process_query(
        session, query, logger, auto=auto, auto_index=index
    )

    if not anime:
        logger.critical("Searcher returned no anime to stream, failed to stream.")
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

    logger.name = "{}/{}".format(provider, logger.name)

    match, provider_module, _ = providers.get_provider(
        providers.append_protocol(anime.get("anime_url"))
    )

    streams = list(
        provider_module.fetcher(
            session, anime.get("anime_url"), helpers.get_check(r), match
        )
    )

    if special:
        streams = list(helpers.special_parser(streams, special))

    if "name" not in anime:
        anime["name"] = (
            provider_module.metadata_fetcher(session, anime.get("anime_url"), match)[
                "titles"
            ]
            or [None]
        )[0] or ""

    content_title = anime["name"]

    content_name = (
        download_folder
        or anime["name"]
        or helpers.choice(helpers.create_random_titles())
    )

    content_dir = Path("./{}/".format(sanitize_filename(content_name.strip())))
    content_dir.mkdir(exist_ok=True)

    total = len(streams)

    logger.debug("Downloading to {!r}.".format(content_dir.as_posix()))

    for count, (stream_urls_caller, episode_number) in enumerate(streams, 1):

        content_title = "E{:02d}".format(int(episode_number))
        stream_urls = helpers.ensure_extraction(session, stream_urls_caller)

        if not stream_urls:
            logger.warning(
                "There were no stream links available at the moment. Ignoring {!r}, retry using a different provider.".format(
                    content_title
                )
            )
            continue

        logger.info(
            "Downloading {!r} [{:02d}/{:02d}, {:02} remaining] ".format(
                content_title, count, total, total - count
            )
        )
        success, reason = helpers.download(
            session,
            logger,
            content_dir,
            content_title,
            stream_urls,
            quality,
            idm=idm,
            retry_timeout=AUTO_RETRY,
            log_level=log_level,
        )

        if not success:
            logger.warning(
                "Could not download {!r} due to: {}. Please retry with other providers.".format(
                    content_title, reason
                )
            )
