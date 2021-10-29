"""
Probably the only 9Anime scraper in the world that does not rely on Selenium or webdrivers to scrape.
"""

import json
from functools import partial

import lxml.html as htmlparser

from ....config import NINEANIME
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(
    NINEANIME, extra_regex=r'/watch/[^&?/]+\.(?P<slug>[^&?/]+)')

def fetcher(session, url, check):

    raise Exception('9Anime is not supported currently!')
