import re

from .stream_url import *

def fetcher(session, url, check):
    
    anime_name = re.match(r'^(?:https?://)?(?:\S+\.)?twist\.moe/a/([^?&/]+)', url).group(1)
    for index, data in enumerate(get_twistmoe_anime_uri(session, anime_name), 1):
        if check(index):
            yield [{'quality': 'unknown', 'stream_url': data.get('stream_url'), 'headers': {'referer': 'https://twist.moe'}}]