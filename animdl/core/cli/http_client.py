import httpx
import logging

from contextlib import suppress

headers = httpx.Headers(
    {
        b"Accept": b"*/*",
        b"Accept-Encoding": b"gzip, deflate",
        b"Connection": b"keep-alive",
        b"Referer": "https://google.com/",
        b"User-Agent": b"animdl/1.4.20",
    }
)


def get_safeoverride(f):
    def inner(*args, **kwargs):
        with suppress():
            return f(*args, **kwargs)
        return

    return inner


class AnimeHttpClient(httpx.Client):

    http_logger = logging.getLogger("animdl-http")


client = AnimeHttpClient(headers=headers, timeout=30.0)

client.__del__ = get_safeoverride(client.__del__)
