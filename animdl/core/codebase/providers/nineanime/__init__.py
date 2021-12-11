from ....config import NINEANIME
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(
    NINEANIME, extra_regex=r'/watch/[^&?/]+\.(?P<slug>[^&?/]+)')

def fetcher(session, url, check, match):

    raise Exception('9Anime is not supported currently!')
