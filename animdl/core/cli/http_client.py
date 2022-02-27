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


class AnimeHttpClient(httpx.Client):

    http_logger = logging.getLogger("animdl-http")


client = AnimeHttpClient(headers=headers, follow_redirects=True, timeout=30.0)
