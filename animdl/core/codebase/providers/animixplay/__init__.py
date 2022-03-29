import regex

from ....config import ANIMIXPLAY
from ...helper import construct_site_based_regex
from .stream_url import fetcher

REGEX = construct_site_based_regex(ANIMIXPLAY, extra_regex=r"/v\d+/([^?&/]+)")

TITLES_REGEX = regex.compile(r'<span class="animetitle">(.+?)</span>')


def metadata_fetcher(session, url, match):
    return {"titles": TITLES_REGEX.findall(session.get(url).text)}
