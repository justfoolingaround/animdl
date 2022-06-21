import logging
import sys
from urllib.parse import quote_plus, urlencode

import httpx

try:
    from .exit_codes import INTERNET_ISSUE
except ImportError:
    from exit_codes import INTERNET_ISSUE

headers = {"User-Agent": "animdl/1.5.84"}

CORS_PROXY = "https://corsproxy.io/"


class AnimeHttpClient(httpx.Client):

    http_logger = logging.getLogger("animdl-http")

    def cf_request(self, method, url, *args, params=None, **kwargs):
        url = CORS_PROXY + "?" + quote_plus(url + "?" + urlencode(params or {}))

        headers = kwargs.pop("headers", {})
        headers.update(referer=url)

        return super().request(method, url, headers=headers, *args, **kwargs)


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
