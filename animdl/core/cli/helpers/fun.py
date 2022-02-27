"""
Fun helpers for the cli.

Credits for the functions:
    create_random_titles: (https://www.ruggenberg.nl/titels.html)
"""

import logging
import os
from contextlib import suppress
from random import choice

import regex
import yarl

from ...__version__ import __core__
from ..http_client import client
from .constants import LABELS, LANGUAGE


terminal_columns = 0

with suppress(Exception):
    terminal_columns = os.get_terminal_size().columns


def line_chop(string: str, max_length, separators=[" ", "\n"]):
    if not string:
        return

    if len(string) <= max_length:
        yield string
        return

    sep, sep_index = max(
        ((_, string[:max_length].rfind(_)) for _ in separators), key=lambda x: x[1]
    )

    if sep_index == -1:
        sep, sep_index = "", max_length

    yield string[:sep_index]
    yield from line_chop(
        string[sep_index + len(sep) :], max_length, separators=separators
    )


def terminal_center(string: str, *, columns=terminal_columns):

    if not columns:
        return string

    def genexp():
        for line in string.splitlines():
            for piece in line_chop(line, columns):
                yield piece.center(columns)

    return "\n".join(genexp())


package_banner = terminal_center(
    """\
justfoolingaround/animdl - v{}
A highly efficient anime downloader and streamer\
""".format(
        __core__
    )
)


update_banner = terminal_center("Update available: {}")


def create_random_titles():

    adjs = LANGUAGE.get("adjective")
    noun = LANGUAGE.get("noun")

    return [
        "{}-{}".format(choice(adjs), choice(noun)),
        "the-{}-{}".format(choice(adjs), choice(noun)),
        "{}-{}".format(choice(noun), choice(noun)),
        "the-{}'s-{}".format(choice(noun), choice(noun)),
        "the-{}-of-the-{}".format(choice(noun), choice(noun)),
        "{}-in-the-{}".format(choice(noun), choice(noun)),
    ]


def to_stdout(message, caller="animdl", *, color_index=36):
    if caller:
        message = "[\x1b[{}m{}\x1b[39m] ".format(color_index, caller) + message
    return print(message)


def stream_judiciary(url):

    try:
        url = yarl.URL(url)
    except Exception:
        return "Unknown [URL Parsing error.]"

    return "{!r} from {}".format(url.name or "Unknown", LABELS.get(url.host, url.host))


def check_for_update(
    *,
    current=__core__,
    git_version_url="https://raw.githubusercontent.com/justfoolingaround/animdl/master/animdl/core/__version__.py"
):
    upstream_version = regex.search(
        r'__core__ = "(.*?)"', client.get(git_version_url).text
    ).group(1)
    return upstream_version == current, upstream_version


def bannerify(f):
    def internal(*args, **kwargs):
        quiet_state = kwargs.get("log_level")
        if quiet_state is not None:
            if quiet_state <= 20:
                print("\x1b[35m{}\x1b[39m".format(package_banner))
                latest, version = check_for_update()
                if not latest:
                    print("\x1b[36m{}\x1b[39m".format(update_banner.format(version)))
            logging.basicConfig(
                level=quiet_state,
                format="[\x1b[35m%(filename)s:%(lineno)d\x1b[39m - %(asctime)s - %(name)s: %(levelname)s] %(message)s",
                filename=kwargs.get("log_file"),
                filemode="a",
            )

            logger = logging.getLoggerClass()
            logger.FILE_STREAM = kwargs.get("log_file")

        return f(*args, **kwargs)

    return internal
