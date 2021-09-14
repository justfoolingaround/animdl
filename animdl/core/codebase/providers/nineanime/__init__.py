"""
Probably the only 9Anime scraper in the world that does not rely on Selenium or webdrivers to scrape.
"""

import json
import re
from functools import partial

import lxml.html as htmlparser

from ....config import NINEANIME
from ...helper import construct_site_based_regex
from .inner import fallback_extraction

REGEX = construct_site_based_regex(
    NINEANIME, extra_regex=r'/watch/[^&?/]+\.(?P<slug>[^&?/]+)')

def fetcher(session, url, check):

    raise Exception('9Anime is not supported currently!')

    slug = ANIME_SLUG.search(url).group("slug")


    ajax_server_response = session.get(
        NINEANIME +
        "ajax/anime/servers",
        params={
            'id': slug,
            },
        )
    data = htmlparser.fromstring(
        ajax_server_response.json().get(
            'html', ''))

    for el in data.xpath('//li/a'):
        en = int(el.get('data-base', 0))
        if check(en):
            yield partial(fallback_extraction, session, json.loads(el.get('data-sources', '{}'))), en
