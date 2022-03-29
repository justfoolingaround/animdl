import contextlib
import logging
import os
import shutil
import subprocess
from collections import defaultdict

import regex
from tqdm import tqdm

executable = "ffmpeg"


def has_ffmpeg():
    return bool(shutil.which(executable))


FFMPEG_EXTENSIONS = ["mpd", "m3u8", "m3u"]


def parse_ffmpeg_duration(dt: str) -> float:
    """
    Converts ffmpeg duration to seconds.

    Returns
    ---

    `float`
    """
    hour, minute, seconds = (float(_) for _ in dt.split(":"))
    return hour * (60**2) + minute * 60 + seconds


def iter_audio(stderr):
    """
    Goes over the audio part of the ffmpeg output and gets the mapping index and
    the frequency.

    Returns
    ---

    `Generator[tuple(str, int)]`

    """

    def it():
        """
        A generator, that is made for sorting and sending to another generator.
        """
        for match in regex.finditer(b"Stream #(\d+):(\d+): Audio:.+ (\d+) Hz", stderr):
            program, stream_id, freq = (_.decode() for _ in match.groups())
            yield "{}:a:{}".format(program, stream_id), int(freq)

    yield from sorted(it(), key=lambda x: x[1], reverse=True)


def analyze_stream(logger: logging.Logger, url: str, headers: dict):
    """
    Converts the output of `ffmpeg -i $URL` to a partial stream info default dict.

    In logging level DEBUG, it shows the ffmpeg output.

    Returns
    ---

    `collections.defaultdict`

    """
    info = defaultdict(lambda: defaultdict(lambda: defaultdict(defaultdict)))

    args = [executable, "-hide_banner"]

    if headers:
        args.extend(
            ("-headers", "\r\n".join("{}:{}".format(k, v) for k, v in headers.items()))
        )

    args.extend(("-i", url))

    logger.debug("Calling PIPE child process for ffmpeg: {}".format(args))
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    stderr = b"".join(iter(process.stdout))

    duration = regex.search(b"Duration: ((?:\d+:)+\d+)", stderr)
    if duration:
        info["duration"] = parse_ffmpeg_duration(duration.group(1).decode())

    audio = [*iter_audio(stderr)]

    for match in regex.finditer(b"Stream #(\d+):(\d+): Video: .+x(\d+)", stderr):
        program, stream_index, resolution = (int(_.decode()) for _ in match.groups())
        info["streams"][program][stream_index]["quality"] = resolution
        info["streams"][program][stream_index]["audio"] = audio

    return info


def iter_quality(quality_dict):
    """
    Iterates over the quality dict returned by `analyze_stream`.
    """
    for programs, streams in quality_dict.get("streams", {}).items():
        for stream, stream_info in streams.items():
            yield "{}:v:{}".format(programs, stream), stream_info.get("quality") or 0, (
                stream_info.get("audio") or [None, 0]
            )[0][0]


def get_last(iterable):
    """
    Gets the last element from the iterable. Pretty self-explanatory.
    """
    expansion = [*iterable]
    if expansion:
        return expansion[-1]


def ffmpeg_to_tqdm(
    logger: logging.Logger, process: subprocess.Popen, duration: int, outfile_name: str
) -> subprocess.CompletedProcess:
    """
    tqdm wrapper for a ffmpeg process.

    Takes a logger `logger`, the ffmpeg child process `process`, duration of stream
    `duration` and the output file's name `outfile_name`

    This uses the simple concept, stream reading using `iter`, after which it takes
    the current time, converts it into seconds and shows the full progress bar.

    In logging level DEBUG, it shows the ffmpeg output.

    Returns
    ---

    `subprocess.Popen` but completed

    """
    progress_bar = tqdm(
        desc="HLS, FFMPEG / GET {}.mkv".format(outfile_name),
        total=duration,
        unit="segment",
    )
    previous_span = 0

    for stream in process.stdout:
        logger.debug("[ffmpeg] {}".format(stream.decode().strip()))
        current = get_last(regex.finditer(b"\stime=((?:\d+:)+\d+)", stream))
        if current:
            in_seconds = (
                parse_ffmpeg_duration(current.group(1).decode()) - previous_span
            )
            previous_span += in_seconds
            progress_bar.update(in_seconds)

    progress_bar.close()
    return process


def ffmpeg_download(
    url: str,
    headers: dict,
    outfile_name: str,
    content_dir,
    preferred_quality=1080,
    log_level=20,
    **opts
) -> int:
    """
    Downloads content using ffmpeg and optionally uses tqdm to wrap the progress
    bar.

    Initally, it fetches content information for the stream using `analyze_stream`.

    Then after, it selects the quality preferred by the user and maps it to the best
    audio. The stream is then passed to tqdm if the logging level is less than INFO.
    If the logging level is greater than INFO, it simply runs the command and waits.

    In logging level DEBUG, it shows the ffmpeg output.

    Returns
    ---

    `int` The ffmpeg child process' return code.

    """

    logger = logging.getLogger("ffmpeg-hls-download[{}.mkv]".format(outfile_name))
    logger.debug("Using ffmpeg to download content.")

    stream_info = analyze_stream(logger, url, headers)

    file = content_dir / ("{}.mkv".format(outfile_name))

    with contextlib.suppress(FileNotFoundError, OSError):
        os.remove(file)

    args = [executable, "-hide_banner"]

    if headers:
        args.extend(
            ("-headers", "\r\n".join("{}:{}".format(k, v) for k, v in headers.items()))
        )

    args.extend(("-i", url, "-c", "copy", file.as_posix()))

    for video, quality, audio in filter(
        lambda x: x[1] <= preferred_quality,
        sorted(iter_quality(stream_info), key=lambda x: x[1], reverse=True),
    ):
        if quality < preferred_quality:
            logger.warning(
                "Could not find the stream of desired quality {}, currently downloading {}.".format(
                    preferred_quality, quality or "an unknown quality"
                )
            )

        child = subprocess.Popen(
            args + ["-map", video, "-map", audio],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if log_level > 20:
            return child.wait()

        return ffmpeg_to_tqdm(
            logger,
            child,
            duration=stream_info.get("duration"),
            outfile_name=outfile_name,
        ).returncode


def merge_subtitles(video_path, out_path, subtitle_paths, log_level=20):

    args = [
        executable,
        "-hide_banner",
        "-i",
        video_path,
        "-c:v",
        "copy",
        out_path,
        "-y",
    ]

    for subtitle in subtitle_paths:
        args.extend(("-i", subtitle))

    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if log_level > 20:
        child.wait()
        return child.returncode

    for _ in iter(child.stdout):
        print("[ffmpeg/submerge] {}".format(_.decode("utf-8").strip()), end="\r")
    child.wait()

    return child.returncode
