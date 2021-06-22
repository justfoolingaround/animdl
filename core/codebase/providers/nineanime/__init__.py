"""
Probably the only 9Anime scraper in the world that does not rely on Selenium or webdrivers to scrape.
"""

import json
import re

import lxml.html as htmlparser

from functools import partial

from ....config import NINEANIME
from ...helper import construct_site_based_regex
from .inner import fallback_extraction

WAF_TOKEN = re.compile(r"(\d{64})")
WAF_SEPARATOR = re.compile(r"\w{2}")

ANIME_SLUG = construct_site_based_regex(NINEANIME, extra_regex=r'/watch/[^&?/]+\.(?P<slug>[^&?/]+)')

def get_waf_token(session):
    with session.get(NINEANIME) as cloudflare_page:
        return ''.join(chr(int(c, 16)) for c in WAF_SEPARATOR.findall(WAF_TOKEN.search(cloudflare_page.text).group(1)))
    
def fetcher(session, url, check):
    
    waf = get_waf_token(session)
    slug = ANIME_SLUG.search(url).group("slug")
    
    access_headers = {
        'cookie': 'waf_cv=%s' % waf,
        'referer': NINEANIME,
    }
    
    with session.get(NINEANIME + "ajax/anime/servers", params={'id': slug}, headers=access_headers) as ajax_server_response:
        data = htmlparser.fromstring(ajax_server_response.json().get('html', ''))
        
    for el in data.xpath('//li/a'):
        en = int(el.get('data-base', 0))
        if check(en):
            yield partial(fallback_extraction, session, json.loads(el.get('data-sources', '{}')), access_headers), en