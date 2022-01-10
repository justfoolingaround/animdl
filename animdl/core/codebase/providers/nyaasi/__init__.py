from functools import partial

import lxml.html as htmlparser

from ....config import NYAASI
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(NYAASI, extra_regex=r"/view/([^?&/]+)")


def fetcher(session, url, check):

    html_element = htmlparser.fromstring(session.get(url).text)
    content_title = html_element.cssselect("h3.panel-title")[0].text_content()

    for n, magnets in enumerate(html_element.cssselect('a[href^="magnet:?"]'), 1):
        yield partial(
            lambda x: [
                {
                    "stream_url": x,
                    "is_torrent": True,
                    "torrent_name": content_title.strip(),
                }
            ],
            magnets.get("href"),
        ), n
