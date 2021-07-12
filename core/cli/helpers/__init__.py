from . import sessions
from .fun import choice, create_random_titles, stream_judiciary, to_stdout, bannerify
from .player import *
from .processors import process_query, get_searcher


def filter_quality(stream_urls, preferred_quality):
    for _ in sorted(stream_urls, reverse=True, key=lambda x: int(x.get('quality') or 0) if x.get('quality') not in ['unknown', 'multi'] else 0):
        q = _.get('quality') or 'unknown'
        if q != 'unknown' and (isinstance(q, int) or q.isdigit()):
            if preferred_quality >= int(q):
                yield _