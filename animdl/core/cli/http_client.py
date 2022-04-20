import logging
import sys

import httpx

try:
    from .exit_codes import INTERNET_ISSUE
except ImportError:
    from exit_codes import INTERNET_ISSUE

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


def httpx_exception():
    hook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        if issubclass(exctype, (httpx.HTTPError)):
            exit(
                AnimeHttpClient.http_logger.critical(
                    "{!r}, this issue originates due to connection issues on your or the servers' side. Retry after troubleshooting connection issues on your side.".format(
                        value
                    )
                )
                or INTERNET_ISSUE
            )

        return hook(exctype, value, traceback)

    sys.excepthook = exception_hook


httpx_exception()

client = AnimeHttpClient(headers=headers, follow_redirects=True, timeout=30.0)
