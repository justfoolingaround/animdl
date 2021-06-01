import re

from .stream_url import *

from ...config import TWIST
from ...helper import construct_site_based_regex

def fetcher(session, url, check):
    anime_name = construct_site_based_regex(TWIST, extra_regex=r'/a/([^?&/]+)').search(url).group(1)
    for index, data in enumerate(get_twistmoe_anime_uri(session, anime_name), 1):
        if check(index):
            yield [{'quality': 'unknown', 'stream_url': data.get('stream_url'), 'headers': {'referer': 'https://twist.moe'}}], index