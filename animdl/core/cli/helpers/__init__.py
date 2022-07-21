import functools
import json
import logging
import traceback

from ...codebase import downloader, extractors
from . import banner, constants, decorators, intelliq, prompts, special
from .player import handle_streamer
from .processors import process_query, provider_searcher_mapping

fe_logger = logging.getLogger("further-extraction")


def inherit_stream_meta(parent, streams, *, exempt=["headers", "stream_url"]):
    for stream in streams:
        stream.update({_: __ for _, __ in parent.items() if _ not in exempt})
        yield stream


def further_extraction(session, stream):
    extractor, options = stream.pop("further_extraction", (None, None))
    if extractor is None:
        return [stream]

    for ext_module, ext in extractors.iter_extractors():
        if getattr(ext_module.extract, "disabled", False):
            continue

        if ext == extractor:
            try:
                return functools.reduce(
                    list.__add__,
                    list(
                        further_extraction(session, inherited_stream)
                        for inherited_stream in inherit_stream_meta(
                            stream,
                            ext_module.extract(
                                session, stream.get("stream_url"), **options
                            ),
                        )
                    ),
                    [],
                )
            except Exception as e:
                fe_logger.error(
                    "Extraction from {!r} failed due to: {!r}.".format(ext, e)
                )

    return []


def ensure_extraction(session, stream_uri_caller):
    for stream in stream_uri_caller():
        if "further_extraction" in stream:
            yield from further_extraction(session, stream)
        else:
            yield stream


def download(
    session, logger, content_dir, outfile_name, stream_urls, quality, **kwargs
):

    downloadable_content = intelliq.filter_quality(list(stream_urls), quality)

    if not downloadable_content:
        return False, "No downloadable content found."

    errors = []

    for download_data in iter(downloadable_content):
        if "further_extraction" in download_data:
            try:
                further_status, further_yield = download(
                    session,
                    logger,
                    content_dir,
                    outfile_name,
                    further_extraction(session, download_data),
                    quality,
                    **kwargs
                )
                if further_status:
                    return further_status, further_yield
                continue
            except Exception as e:
                logger.critical(
                    "Could not extract from the stream due to {!r}. falling back to other streams.".format(
                        e
                    )
                )
                continue

        content_url = download_data.get("stream_url")
        content_headers = download_data.get("headers")

        try:
            return True, downloader.handle_download(
                session,
                content_url,
                content_headers,
                content_dir,
                outfile_name,
                preferred_quality=quality,
                subtitles=download_data.get("subtitle", []),
                **kwargs
            )
        except Exception as e:
            logger.critical(
                "Oops, due to {!r}, this stream has been rendered unable to download.".format(
                    e
                )
            )

            errors.append((download_data, e, traceback.format_exc()))

    logger.critical(
        "No downloads were done. Use log level DEBUG or, -ll 0 to get complete tracebacks for the failed downloads."
    )

    for count, (download_data, exception, tb) in enumerate(errors, 1):
        logger.debug(
            json.dumps(
                {
                    "download_count": count,
                    "data": download_data,
                    "exception": repr(exception),
                    "traceback": tb,
                },
                indent=4,
            )
        )

    return False, "All stream links were undownloadable."
