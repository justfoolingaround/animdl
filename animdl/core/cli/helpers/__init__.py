import enum
import logging
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, Generator, Optional, Tuple
    import pathlib

    import httpx

from ...codebase import downloader, extractors
from . import (
    aniskip,
    banner,
    constants,
    decorators,
    intelliq,
    player,
    prompts,
    special,
    stream_handlers,
)
from .processors import process_query, provider_searcher_mapping

further_extraction_logger = logging.getLogger("further-extraction")


def further_extraction(session: "httpx.Client", parent_stream: "Dict[str, Any]"):
    extractor, options = parent_stream.pop("further_extraction", (None, None))

    if extractor is None:
        return (yield parent_stream)

    for ext_module, ext in extractors.iter_extractors():
        if ext != extractor or getattr(ext_module.extract, "disabled", False):
            continue

        try:
            for stream in ext_module.extract(
                session, parent_stream.get("stream_url"), **options
            ):
                child = parent_stream.copy()
                child.update(stream)

                yield from further_extraction(session, child)

        except Exception as exception:
            further_extraction_logger.error(
                f"Extraction from {ext!r} failed due to: {exception!r}."
            )


def ensure_extraction(session, stream_uri_caller):
    for stream in stream_uri_caller():
        if "further_extraction" in stream:
            yield from further_extraction(session, stream)
        else:
            yield stream


class SafeCaseEnum(enum.Enum):
    NO_CONTENT_FOUND = enum.auto()
    DOWNLOADED = enum.auto()

    EXTRACTION_ERROR = enum.auto()
    DOWNLOADER_EXCEPTION = enum.auto()


def safe_download_callback(
    session: "httpx.Client",
    logger: "logging.Logger",
    stream_urls: "Generator[Dict[str, Any], None, None]",
    quality: str,
    expected_download_path: "pathlib.Path",
    use_internet_download_manager: bool = False,
    retry_timeout: "Optional[int]" = None,
    log_level: "Optional[int]" = None,
    **kwargs,
) -> "Tuple[SafeCaseEnum, Optional[BaseException]]":
    flattened_streams = list(stream_urls)

    try:
        streams = intelliq.filter_quality(flattened_streams, quality)
    except Exception as exception:
        return SafeCaseEnum.EXTRACTION_ERROR, exception

    if not streams:
        return SafeCaseEnum.NO_CONTENT_FOUND, None

    for stream in streams:
        needs_further_extraction = "further_extraction" in stream

        if needs_further_extraction:
            status, potential_error = safe_download_callback(
                session,
                logger,
                further_extraction(session, stream),
                quality,
                expected_download_path,
                use_internet_download_manager,
                retry_timeout,
                log_level,
                **kwargs,
            )

            if status == SafeCaseEnum.DOWNLOADED:
                return status, potential_error

            if status == SafeCaseEnum.NO_CONTENT_FOUND:
                logger.debug(f"Could not find streams on further extraction, skipping.")
                continue

            if status == SafeCaseEnum.EXTRACTION_ERROR:
                logger.error(
                    f"Could not extract streams from further extraction due to an error: {potential_error}, skipping."
                )
                continue

            if status == SafeCaseEnum.DOWNLOADER_EXCEPTION:
                logger.error(
                    f"Could not download streams from further extraction due to multiple errors, skipping."
                )
                continue

        else:
            try:
                downloader.handle_download(
                    session=session,
                    url=stream["stream_url"],
                    expected_download_path=expected_download_path,
                    use_internet_download_manager=use_internet_download_manager,
                    headers=stream.get("headers"),
                    preferred_quality=quality,
                    subtitles=stream.get("subtitle"),
                    **kwargs,
                )
                return SafeCaseEnum.DOWNLOADED, None

            except Exception as download_exception:
                logger.error(
                    f"Could not download stream due to an error: {download_exception!r}, skipping."
                )
                logger.debug(f"Traceback for the above error: {traceback.format_exc()}")

        logger.critical(
            "Could not download any streams. Use the project with 0 log level to view errors for debugging and bug reporting purposes."
        )

        return SafeCaseEnum.NO_CONTENT_FOUND, None
