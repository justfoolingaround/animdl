"""
animdl: Utilities for the perfect HTTP disguise. 
"""

import sys
import typing as t
from urllib.parse import quote, urlencode

from animdl.core.__version__ import __core__

if t.TYPE_CHECKING:
    import logging

    import httpx

CORS_PROXY = "https://corsproxy.io/"


def get_user_agent():
    """
    Returns the user agent to be used in the requests.

    The project will not be detected as a bot so
    standardising is better for the web developers.

    :return: The user agent.
    """
    return f"animdl/{__core__} ({sys.platform})"


def cors_proxify(
    session: "httpx.Client",
    method: str,
    url: str,
    *args,
    params=None,
    headers=None,
    **kwargs,
):
    """
    CORS Proxy is a service that forwards the requests
    to the target website and returns the response.

    This may also bypass geo-restrictions.

    :param session: The session to use for the request.
    :param method: The method to use for the request.
    :param url: The URL to send the request to.
    :param args: The arguments to pass to the request.
    :param params: The parameters to pass to the request.
    :param headers: The headers to pass to the request.
    :param kwargs: The keyword arguments to pass to the request.

    :return: The response from the request.
    """
    if params is not None:
        url += "?" + urlencode(params)

    cors_url = CORS_PROXY + "?" + quote(url)

    if headers is None:
        headers = {}

    headers.update(referer=url)
    return session.request(method, cors_url, headers=headers, *args, **kwargs)


def integrate_ddg_bypassing(session: "httpx.Client", *hosts: str):
    """
    DDoS Guard is a service that protects websites from
    DDoS attacks. It does this by blocking the requests
    from the bots and crawlers. This function integrates
    the bypassing of the DDoS Guard into the session.

    :param session: The session to integrate the bypassing into.
    :param hosts: The hosts to bypass the DDoS Guard for.

    :return: None
    """
    for host in hosts:
        session.cookies.set(
            "__ddg2_",
            "YW5pbWRsX3NheXNfaGkNCg.",
            domain=host,
        )


def setup_global_http_exception_hook(
    exit_code: int,
    http_error_baseclass: t.Type["httpx.HTTPError"],
    logger: t.Optional["logging.Logger"] = None,
    msg: str = (
        "{value!r}, this issue originates due to connection issues on your or the server's side. "
        "Retry after troubleshooting connection issues on your system."
    ),
):
    """
    Sets up the global exception hook for any HTTP exceptions
    for graceful exit.

    :return: None
    """
    hook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        if issubclass(exctype, http_error_baseclass):
            if logger is not None:
                logger.error(
                    msg.format(value=value),
                    exc_info=True,
                )

            exit(exit_code)

        return hook(exctype, value, traceback)

    sys.excepthook = exception_hook


if __name__ == "__main__":
    import httpx

    client = httpx.Client(
        headers={
            "User-Agent": get_user_agent(),
        },
        timeout=30.0,
        follow_redirects=True,
    )

    integrate_ddg_bypassing(
        client,
        ".marin.moe",
        ".haho.moe",
    )

    assert (
        client.get("https://marin.moe/").status_code == 200
    ), "Could not bypass DDoS Guard."
    assert (
        client.get(
            "http://www.crunchyroll.com/",
            headers={
                "Referer": "",
            },
        ).status_code
        == 200
    ), "Could not bypass cloudflare."
    assert (
        cors_proxify(
            client,
            "GET",
            "https://www.animeout.xyz/",
        ).status_code
        == 200
    ), "Could not validate CORS Proxy."

    print("HTTP Client is primed.", file=sys.stderr)
