import lxml.html as htmlparser

from ....config import HAHO
from ...helper import construct_site_based_regex
from ..tenshimoe import fetcher as tenshimoe_fetcher
from ..tenshimoe import metadata_fetcher as tenshimoe_metadata_fetcher

REGEX = construct_site_based_regex(HAHO, extra_regex=r"/anime/([^?&/]+)")


def post_processor(session, stream_page):
    def _get_quality(quality_string):
        q = quality_string.rstrip("pP")
        if q.isdigit():
            return int(q)
        return None

    yield from (
        {"stream_url": _.get("src"), "quality": _get_quality(_.get("title"))}
        for _ in htmlparser.fromstring(stream_page).cssselect("source")
    )


def fetcher(*args, **kwargs):
    yield from tenshimoe_fetcher(
        *args, **kwargs, post_processor=post_processor, domain=HAHO
    )


def metadata_fetcher(*args, **kwargs):
    return tenshimoe_metadata_fetcher(*args, **kwargs, domain=HAHO)
