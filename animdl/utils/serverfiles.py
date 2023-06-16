import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING

from .optopt import regexlib

if TYPE_CHECKING:
    from typing import Optional

CONTENT_DISP_RE = regexlib.compile(r'filename=(?:"(.+?)"|([^;]+))')


def guess_from_path(path: str) -> "Optional[str]":
    """
    Attempts to guess the filename from the path.
    """
    return Path(path).name


def guess_from_content_disposition(content_disposition: str) -> "Optional[str]":
    """
    Attempts to guess the filename from the content disposition header.
    """
    match = CONTENT_DISP_RE.search(content_disposition)

    if match is None:
        return None

    return guess_from_path(match.group(1) or match.group(2))


def guess_from_content_type(filename, content_type):
    """
    Attempts to guess the filename from the content type header.
    """

    guessed_extension = mimetypes.guess_extension(content_type)

    if guessed_extension is None:
        return filename

    return filename + guessed_extension
