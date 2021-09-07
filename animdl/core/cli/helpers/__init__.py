from . import sessions
from .fun import choice, create_random_titles, stream_judiciary, to_stdout, bannerify
from .player import *
from .processors import process_query, get_searcher

import yarl


def get_extension(url):
    url = yarl.URL(url)
    position = url.name.find('.')
    if position == -1:
        return ''
    return url.name[position + 1:]


def filter_urls(stream_urls, *, download=False,
                supported_formats=['m3u8', 'mp4', 'php', 'm3u']):
    for _ in sorted(
        stream_urls,
        reverse=True,
        key=lambda x: int(
            x.get('quality') or 0) if x.get('quality') not in [
            'unknown',
            'multi'] else 0):

        if not get_extension(_.get('stream_url')) in supported_formats:
            continue
        if download and _.get('download') is False:
            continue
        yield _
        q = _.get('quality') or 'unknown'


def filter_quality(stream_urls, preferred_quality, *, download=False,
                   supported_formats=['m3u8', 'mp4', 'php', 'm3u']):
    for _ in filter_urls(stream_urls, download=False, supported_formats=[
                         'm3u8', 'mp4', 'php', 'm3u']):
        q = _.get('quality') or 'unknown'
        if q != 'unknown' and (isinstance(q, int) or q.isdigit()):
            if preferred_quality >= int(q):
                yield _
