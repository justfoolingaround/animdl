"""
Torrent client!
"""

import time

import httpx
import regex
from tqdm import tqdm

MAGNET_URI_REGEX = regex.compile(r"btih:([^&?]+)")


def is_supported(session, endpoint):
    try:
        session.get(endpoint + "/api/v2")
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return False
    return True


def authenticate(session, endpoint, login_data):
    return session.post(endpoint + "/api/v2/auth/login", data=login_data).text == "Ok."


def wrap_with_tqdm(session, btih, endpoint, torrent_name, log_level):
    """
    Do not use this in an unauthenticated scenario.
    """

    uri = endpoint + "/api/v2/torrents/properties?hash={}".format(btih)
    torrent = session.get(uri).json()

    progress_bar = tqdm(
        disable=log_level > 20,
        total=torrent.get("total_size", 0),
        unit="B",
        unit_divisor=1024,
        unit_scale=True,
        desc="qBittorrent / {}".format(torrent_name),
        initial=torrent.get("total_downloaded", 0),
    )
    current = torrent.get("total_downloaded", 0)

    while torrent.get("eta") > 0:
        torrent = session.get(uri).json()
        progress_bar.update(torrent.get("total_downloaded", 0) - current)
        current = torrent.get("total_downloaded")

        progress_bar.total = progress_bar.total or torrent.get("total_size", 0)

        time.sleep(1)


def download_torrent(
    _, magnet_uri, content_dir, torrent_name, endpoint, login_data, *, log_level=20
):
    """
    Enqueues the torrent to the qBittorrent client. If already there, doesn't but shows the status of the torrent.
    """
    session = httpx.Client()

    auth = authenticate(session, endpoint, login_data)

    if not auth:
        raise Exception("Invalid credentials for qBittorrent server.")

    magnet_match = MAGNET_URI_REGEX.search(magnet_uri)
    if not magnet_match:
        raise Exception("Not a valid magnet url.")

    btih = magnet_match.group(1)

    existent = session.post(
        endpoint + "/api/v2/torrents/properties", params={"hash": btih}
    )

    if existent.status_code in [404, 400]:
        status = session.post(
            endpoint + "/api/v2/torrents/add",
            data={"urls": magnet_uri, "savepath": content_dir.resolve().as_posix()},
        ).text

        if status == "Fails.":
            raise Exception(
                "Could not add to the client: ({!r}, {!r})".format(
                    magnet_uri, content_dir
                )
            )

    return wrap_with_tqdm(session, btih, endpoint, torrent_name, log_level)
