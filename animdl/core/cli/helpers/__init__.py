import functools
import logging
import traceback

import regex
from click import prompt

from ...codebase import downloader, extractors
from .fun import (bannerify, choice, create_random_titles, stream_judiciary,
                  to_stdout)
from .intelliq import filter_quality
from .player import *
from .processors import get_searcher, process_query
from .searcher import link as processor_link

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
        if ext == extractor:
            try:
                return functools.reduce(
                    lambda x, y: x + y,
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


def get_range_conditions(range_string):
    for matches in regex.finditer(r"(?:([0-9]*)[:\-.]([0-9]*)|([0-9]+))", range_string):
        start, end, singular = matches.groups()
        if start and end and int(start) > int(end):
            start, end = end, start
        yield (lambda x, s=singular: int(s) == x) if singular else (
            lambda x: True
        ) if not (start or end) else (
            lambda x, s=start: x >= int(s)
        ) if start and not end else (
            lambda x, e=end: x <= int(e)
        ) if not start and end else (
            lambda x, s=start, e=end: int(s) <= x <= int(e)
        )


def get_check(range_string):
    if not range_string:
        return lambda *args, **kwargs: True
    return lambda x: any(
        condition(x) for condition in get_range_conditions(range_string)
    )


def ask(log_level, **prompt_kwargs):

    if log_level > 20:
        return prompt_kwargs.get("default")

    return prompt(**prompt_kwargs)


DOWNLOAD_ERROR_MESSAGE = """
\x1b[34mDownload failure #{0:02d}\x1b[39m

Download Arguments: {1}

Raw exception: {2!r}

Complete traceback: {3}\
"""


def download(
    session, logger, content_dir, outfile_name, stream_urls, quality, **kwargs
):
    downloadable_content = filter_quality(stream_urls, quality)

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
        logger.debug(DOWNLOAD_ERROR_MESSAGE.format(count, download_data, exception, tb))

    return False, "All stream links were undownloadable."
