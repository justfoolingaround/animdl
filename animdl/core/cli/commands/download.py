import logging
from pathlib import Path

import click

from ...__version__ import __core__
from ...codebase import providers, sanitize_filename
from ...config import (
    AUTO_RETRY,
    CHECK_FOR_UPDATES,
    DEFAULT_PROVIDER,
    DOWNLOAD_DIRECTORY,
    QUALITY,
)
from .. import exit_codes, helpers, http_client


@click.command(name="download", help="Download your favorite anime by query.")
@helpers.decorators.content_fetch_options(
    default_quality_string=QUALITY,
)
@helpers.decorators.download_options(
    default_download_dir=DOWNLOAD_DIRECTORY,
)
@helpers.decorators.automatic_selection_options()
@helpers.decorators.logging_options()
@helpers.decorators.setup_loggers()
@helpers.decorators.banner_gift_wrapper(
    http_client.client, __core__, check_for_updates=CHECK_FOR_UPDATES
)
def animdl_download(
    query, special, quality, download_dir, idm, index, log_level, **kwargs
):
    r = kwargs.get("range")

    logger = logging.getLogger("downloader")

    anime, provider = helpers.process_query(
        http_client.client, query, logger, auto_index=index, provider=DEFAULT_PROVIDER
    )

    if not anime:
        logger.critical("Searcher returned no anime to stream, failed to stream.")
        raise SystemExit(exit_codes.NO_CONTENT_FOUND)

    logger.name = "{}/{}".format(provider, logger.name)

    match, provider_module, _ = providers.get_provider(
        providers.append_protocol(anime.get("anime_url"))
    )

    streams = list(
        provider_module.fetcher(http_client.client, anime.get("anime_url"), r, match)
    )

    if special:
        streams = list(helpers.special.special_parser(streams, special))

    download_directory = Path(download_dir).resolve(strict=True)
    content_name = sanitize_filename(anime["name"])

    content_dir = download_directory / content_name
    content_dir.mkdir(exist_ok=True)

    logger.debug(f"Download directory: {content_dir.as_posix()!r}")
    total = len(streams)

    for count, (stream_urls_caller, episode_number) in enumerate(streams, 1):

        content_title = "E{:02d}".format(int(episode_number))
        stream_urls = helpers.ensure_extraction(http_client.client, stream_urls_caller)

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
            http_client.client,
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
