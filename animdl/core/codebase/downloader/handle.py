import logging
import os
import pathlib
import tempfile
import typing

import httpx
from tqdm import tqdm

from animdl.utils import media_downloader, serverfiles

from ...config import FFMPEG_EXECUTABLE, FFMPEG_HLS, FFMPEG_SUBMERGE, THREADED_DOWNLOAD
from .ffmpeg import FFMPEG_EXTENSIONS, ffmpeg_download, has_ffmpeg, merge_subtitles
from .hls import HLS_STREAM_EXTENSIONS, hls_yield

if FFMPEG_EXECUTABLE:
    ffmpeg_executable = FFMPEG_EXECUTABLE


DEFAULT_MEDIA_EXTENSION = "mp4"
POSSIBLE_VIDEO_EXTENSIONS = (
    "mp4",
    "mkv",
    "webm",
    "flv",
    "avi",
    "mov",
    "wmv",
    "mpg",
    "mpeg",
    "m4v",
    "3gp",
    "3g2",
    "m2v",
    "m4v",
    "f4v",
    "f4p",
    "f4a",
    "ts",
    "m3u8",
    "m3u",
    "mpd",
    "ism",
    "ismv",
    "dash",
    "av1",
)


EXEMPT_EXTENSIONS = ["mpd"]


def sanitize_filename(f):
    return "".join(" - " if _ in '<>:"/\\|?*' else _ for _ in f).strip()


def standard_download(
    session: httpx.Client,
    url: str,
    expected_download_path: pathlib.Path,
    content_size: "typing.Optional[int]" = None,
    headers: "typing.Optional[dict]" = None,
    ranges: bool = True,
    log_level: int = 20,
    retry_timeout: float = 5.0,
    method="GET",
):
    expected_download_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"downloader/standard[{expected_download_path.name}]")

    with open(expected_download_path, "ab") as download_io:
        position = download_io.tell()

        if position:
            if not ranges:
                logger.critical(
                    "Stream does not support ranged downloading, the previous download cannot be continued."
                )
                download_io.seek(0)
                position = 0

            if THREADED_DOWNLOAD:
                logger.critical(
                    "Download will not be continued as continuation is not supported in threaded downloads."
                )
                download_io.seek(0)
                position = 0

        progress_bar = tqdm(
            desc=f"{method} / {expected_download_path.name}",
            total=content_size,
            disable=log_level > 20,
            initial=position,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

        downloader = media_downloader.MultiConnectionDownloader(
            session,
            method,
            url,
            headers=headers,
            retry_timeout=retry_timeout,
            progress_bar=progress_bar,
        )

        downloader.allocate_downloads(
            download_io,
            content_size,
            start_at=position,
            threaded=ranges and THREADED_DOWNLOAD,
        )

    progress_bar.close()
    return expected_download_path


def hls_download(
    session: httpx.Client,
    url: str,
    expected_download_path: pathlib.Path,
    headers: dict = {},
    method="GET",
    **opts,
):
    content_path = expected_download_path.with_suffix(".mpeg")
    index_holder = expected_download_path.with_suffix(".index")
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
            desc=f"HLS {method} / {content_path.name}",
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
                content_path, stddev / (1024**2)
            )
            progress_bar.update(size)

            istream.write(str(current or 0 + 1))
            istream.seek(0)
            istream.flush()

            tsstream.write(stream)

    progress_bar.close()
    os.remove(index_holder)
    return content_path


def idm_download(url, headers, expected_download_path: pathlib.Path, **opts):
    from .idmanlib import wait_until_download as idmdl

    idmdl(
        url,
        headers=headers or {},
        download_folder=expected_download_path.parent,
        filename=expected_download_path.name,
    )
    return expected_download_path


def subautomatic(f: "handle_download"):
    def __inner__(
        session: httpx.Client,
        url: str,
        expected_download_path: pathlib.Path,
        use_internet_download_manager=False,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        **opts,
    ):
        logger = logging.getLogger("ffmpeg/submerge")

        subtitles = opts.pop("subtitles", [])

        content_path = f(
            session=session,
            url=url,
            expected_download_path=expected_download_path,
            use_internet_download_manager=use_internet_download_manager,
            headers=headers,
            **opts,
        )  # type: pathlib.Path

        if not subtitles or not FFMPEG_SUBMERGE:
            return content_path

        locations = []

        for n, subtitle in enumerate(subtitles):
            prefetch_response = media_downloader.prefetch(
                session, subtitle, opts.get("method", "GET"), headers=headers
            )

            content_disposition = prefetch_response.headers.get("Content-Disposition")

            if content_disposition:
                server_filename = serverfiles.guess_from_content_disposition(
                    content_disposition
                )
            else:
                content_type = prefetch_response.headers.get("Content-Type")

                if content_type:
                    server_filename = serverfiles.guess_from_content_type(
                        "file", content_type
                    )

                else:
                    server_filename = serverfiles.guess_from_path(
                        prefetch_response.url.path
                    )

            download_location = content_path.parent / (
                f"{content_path.name}_sub_{n}_" + (server_filename or "")
            )

            standard_download(
                session,
                url,
                download_location,
                headers=headers,
                log_level=opts.get("log_level", 20),
                retry_timeout=opts.get("retry_timeout", 5),
            )

            locations.append(download_location.resolve().as_posix())

        if (not has_ffmpeg()) or not FFMPEG_SUBMERGE:
            logger.info("ffmpeg is unavailable, skipping subtitle merging.")
            return content_path

        out_path = content_path.with_name(
            content_path.name + "_submerged" + content_path.suffix
        )

        ffmpeg_returncode = merge_subtitles(
            content_path,
            out_path,
            locations,
            log_level=opts.get("log_level", 20),
        )

        if ffmpeg_returncode:
            logger.warning(
                f"Got a non-zero return code {ffmpeg_returncode} from ffmpeg, the original file will not be erased in case of merge failure."
            )
            return content_path

        content_path.unlink(missing_ok=True)

        try:
            out_path.rename(content_path)
        except OSError:
            logger.warning(
                f"Failed to rename {out_path} to {content_path}, the converted file will not be erased in case of merge failure."
            )

        return out_path

    return __inner__


@subautomatic
def handle_download(
    session: httpx.Client,
    url: str,
    expected_download_path: pathlib.Path,
    use_internet_download_manager=False,
    headers: typing.Optional[typing.Dict[str, str]] = None,
    **opts,
):
    download_handling_logger = logging.getLogger("animdl/download-handler")

    prefetch_response = media_downloader.prefetch(
        session, opts.get("method", "GET"), url, headers=headers
    )

    content_disposition = prefetch_response.headers.get("Content-Disposition")

    server_filename = None

    if server_filename is None and content_disposition:
        server_filename = serverfiles.guess_from_content_disposition(
            content_disposition
        )

    content_type = prefetch_response.headers.get("Content-Type")

    if server_filename is None and content_type:
        server_filename = serverfiles.guess_from_content_type("file", content_type)

    if server_filename is None:
        server_filename = serverfiles.guess_from_path(prefetch_response.url.path)

    content_range = prefetch_response.headers.get("Content-Range")

    if content_range is not None:
        content_size = int(content_range.split("/", 1)[1])
    else:
        content_size = None

    ranges = prefetch_response.status_code == 206 or (
        prefetch_response.headers.get("Accept-Ranges") == "bytes"
    )

    if server_filename and "." in server_filename:
        _, extension = server_filename.rsplit(".", 1)
    else:
        extension = None

    if extension not in POSSIBLE_VIDEO_EXTENSIONS:
        download_handling_logger.warn(
            f"The server gave filename as {server_filename!r} but the project is unsure whether this format is what it intends to use. "
            f"Hence, the downloader will be using {DEFAULT_MEDIA_EXTENSION!r}, the file format may be different or the file may end up as corrupted"
            ", in those cases, do report at project's issue tracker."
        )
        extension = DEFAULT_MEDIA_EXTENSION

    expected_download_path = expected_download_path.with_suffix(f".{extension}")

    download_handling_logger.info(
        f"Server filename: {server_filename!r}, project inferred: {expected_download_path.name!r}",
    )

    expected_download_path.parent.mkdir(parents=True, exist_ok=True)

    if FFMPEG_HLS and (extension in FFMPEG_EXTENSIONS and has_ffmpeg()):
        return_code = ffmpeg_download(url, headers, expected_download_path, **opts)

        if return_code:
            raise Exception(
                f"ffmpeg exited with non-zero return code {return_code}, download failed."
            )

        return expected_download_path.with_suffix(".mkv")

    if extension in EXEMPT_EXTENSIONS:
        raise Exception(
            "Download extension {!r} requires custom downloading which is not supported yet.".format(
                extension
            )
        )

    if extension in HLS_STREAM_EXTENSIONS:
        return hls_download(session, url, expected_download_path, headers or {}, **opts)

    if use_internet_download_manager:
        return idm_download(url, headers or {}, expected_download_path, **opts)

    return standard_download(
        session,
        url,
        expected_download_path,
        content_size,
        headers,
        ranges,
        log_level=opts.get("log_level", 20),
        retry_timeout=opts.get("retry_timeout", 5.0),
    )
