import logging
import os
import pathlib
import time

import httpx
import regex
import yarl
from tqdm import tqdm

from ...config import FFMPEG_EXECUTABLE, FFMPEG_HLS, FFMPEG_SUBMERGE
from .content_mt import mimetypes
from .ffmpeg import (FFMPEG_EXTENSIONS, ffmpeg_download, has_ffmpeg,
                     merge_subtitles)
from .hls import HLS_STREAM_EXTENSIONS, hls_yield

if FFMPEG_EXECUTABLE:
    ffmpeg_executable = FFMPEG_EXECUTABLE

EXEMPT_EXTENSIONS = ["mpd"]
CONTENT_DISP_RE = regex.compile(r'filename=(?:"(.+?)"|([^;]+))')


def sanitize_filename(f):
    return "".join(" - " if _ in '<>:"/\\|?*' else _ for _ in f).strip()


def ext_from_filename(filename):
    position = filename.rfind(".")
    if position == -1:
        return ""
    return filename[position + 1 :]


def get_extension(url):
    url = yarl.URL(url)
    return ext_from_filename(url.name)


def guess_extension(content_type):
    if not content_type:
        return ""

    for _, cd, extension in mimetypes:
        if cd == content_type:
            return (extension or "").lstrip(".")


def ext_from_content_disposition(content_disposition):
    match = CONTENT_DISP_RE.search(content_disposition)

    if not match:
        return ""

    return ext_from_filename(match.group(1) or match.group(2))


def process_url(session, url, headers={}):
    """
    Get the extension, content size and range downloadability forehand.

    Returns:

    `str`, `int`, `bool`
    """
    response = session.head(url, headers=headers)
    response_headers = response.headers

    extension = (
        ext_from_content_disposition(
            response_headers.get("content-disposition", "") or ""
        )
        or guess_extension(response_headers.get("content-type", ""))
        or get_extension(url)
        or get_extension(str(response.url))
    ).lower()

    return (
        extension,
        int(response_headers.get("content-length") or 0),
        "bytes" in response_headers.get("accept-ranges", ""),
    )


def standard_download(
    session: httpx.Client,
    url: str,
    content_dir: pathlib.Path,
    outfile_name: str,
    extension: str,
    content_size: int,
    headers: dict = {},
    ranges=True,
    **opts
):
    file = "{}.{}".format(outfile_name, extension)

    logger = logging.getLogger("downloader/standard[{}]".format(file))
    out_path = content_dir / pathlib.Path(sanitize_filename(file))

    if not ranges:
        logger.critical(
            "Stream does not support ranged downloading; failed downloads cannot be continued."
        )

    with open(out_path, "ab") as outstream:
        downloaded = outstream.tell() if ranges else 0
        progress_bar = tqdm(
            desc="GET / {}".format(file),
            total=content_size,
            disable=opts.get("log_level", 20) > 20,
            initial=downloaded,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )
        while content_size > downloaded:
            temporary_headers = headers.copy()
            if ranges:
                temporary_headers.update({"Ranges": "bytes={}-".format(downloaded)})
            try:
                with session.stream("GET", url, headers=headers) as http_stream:
                    http_stream.raise_for_status()

                    for chunks in http_stream.iter_bytes():
                        size = len(chunks)
                        outstream.write(chunks)
                        progress_bar.update(size)
                        downloaded += size
            except httpx.RequestError as e:
                if not ranges:
                    downloaded = 0
                    outstream.seek(0)
                    progress_bar.clear()
                else:
                    outstream.flush()
                logger.error("Downloading error due to {!r}, retrying.".format(e))
                time.sleep(opts.get("retry_timeout") or 5.0)

    progress_bar.close()


def hls_download(
    session: httpx.Client,
    url: str,
    content_dir: pathlib.Path,
    outfile_name: str,
    headers: dict = {},
    **opts
):

    sanitized = sanitize_filename(outfile_name)
    content_path = content_dir / "{}.ts".format(sanitized)
    index_holder = content_dir / "{}.partialts".format(sanitized)
    index = 1

    if index_holder.exists():
        with open(index_holder, "r") as ih:
            index = int(ih.read() or 1)

    sizes = []
    with open(content_path, "ab") as tsstream, open(index_holder, "w+") as istream:
        downloaded = tsstream.tell()
        if downloaded:
            sizes.extend([downloaded / index] * index)
        progress_bar = tqdm(
            desc="HLS GET / {}.ts".format(outfile_name),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            initial=downloaded,
            disable=opts.get("log_level", 20) > 20,
        )

        for content in hls_yield(
            session,
            [{"stream_url": url, "headers": headers}],
            opts.get("preferred_quality") or 1080,
            opts.get("retry_timeout") or 5,
            continuation_index=index,
        ):
            stream = content.get("bytes")
            total = content.get("total")
            current = content.get("current")

            size = len(stream)
            sizes.append(size)

            mean = sum(sizes) / len(sizes)
            stddev = (sum(abs(mean - s) ** 2 for s in sizes) / len(sizes)) ** 0.5

            progress_bar.total = mean * total
            progress_bar.desc = "HLS GET / {}.ts [± {:.3f} MB]".format(
                outfile_name, stddev / (1024 ** 2)
            )
            progress_bar.update(size)

            istream.write(str(current or 0 + 1))
            istream.seek(0)
            istream.flush()

            tsstream.write(stream)

    progress_bar.close()
    os.remove(index_holder)


def idm_download(url, headers, content_dir, outfile_name, extension, **opts):
    file = "{}.{}".format(outfile_name, extension)
    from .idmanlib import wait_until_download as idmdl

    idmdl(url, headers=headers or {}, download_folder=content_dir, filename=file)


def subautomatic(f):

    def __inner__(session, url, headers, content_dir, outfile_name, *args, **kwargs):
        logger = logging.getLogger("ffmpeg/submerge")

        subtitles = kwargs.pop("subtitles", [])

        callback = f(session, url, headers, content_dir, outfile_name, *args, **kwargs)

        if not subtitles:
            return

        if (not has_ffmpeg()) or not FFMPEG_SUBMERGE:
            logger.debug("{!r} will not be merged.".format(subtitles))
            for count, subtitle in enumerate(subtitles, 1):
                handle_download(
                    session,
                    subtitle,
                    headers=headers,
                    content_dir=content_dir,
                    outfile_name="{}_SUB_{}".format(outfile_name, count),
                )
            return callback

        extension, _, _ = process_url(session, url, headers)
        resolved_path = (
            content_dir / "{}.{}".format(outfile_name, extension)
        ).resolve()
        subout_path = (
            content_dir / "{} [CC].{}".format(outfile_name, extension)
        ).resolve()

        ffmpeg_returncode = merge_subtitles(
            resolved_path, subout_path, subtitles, log_level=kwargs.get("log_level", 20)
        )

        if ffmpeg_returncode:
            return (
                logger.warning(
                    "Got a non-zero return code {} from ffmpeg, the original file will not be erased in case of merge failure.".format(
                        ffmpeg_returncode
                    )
                )
                or callback
            )

        try:
            os.remove(resolved_path)
        except FileNotFoundError:
            pass

        try:
            os.rename(subout_path, resolved_path)
        except FileNotFoundError:
            pass

        return callback

    return __inner__


@subautomatic
def handle_download(
    session, url, headers, content_dir, outfile_name, idm=False, **opts
):

    extension, content_size, ranges = process_url(session, url, headers)

    if FFMPEG_HLS and (extension in FFMPEG_EXTENSIONS and has_ffmpeg()):
        return ffmpeg_download(url, headers, outfile_name, content_dir, **opts)

    if extension in EXEMPT_EXTENSIONS:
        raise Exception(
            "Download extension {!r} requires custom downloading which is not supported yet.".format(
                extension
            )
        )

    if extension in HLS_STREAM_EXTENSIONS:
        return hls_download(
            session, url, content_dir, outfile_name, headers or {}, **opts
        )

    if idm:
        return idm_download(
            url, headers or {}, content_dir.resolve(), outfile_name, extension, **opts
        )

    return standard_download(
        session,
        url,
        content_dir,
        outfile_name,
        extension,
        content_size,
        headers or {},
        ranges,
        **opts
    )
