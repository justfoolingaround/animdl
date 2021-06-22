from functools import partial
import re

from .stream_url import *

from ....config import TWIST
from ...helper import construct_site_based_regex

def fetcher(session, url, check):
    anime_name = construct_site_based_regex(TWIST, extra_regex=r'/a/([^?&/]+)').search(url).group(1)
    for index, data in enumerate(get_twistmoe_anime_uri(session, anime_name), 1):
        if check(index):
            yield partial(lambda u: ([{'quality': 'unknown', 'stream_url': u, 'headers': {'referer': 'https://twist.moe'}}]), data.get('stream_url')), index