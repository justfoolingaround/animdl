"""
Probably the only 9Anime scraper in the world that does not rely on Selenium or webdrivers to scrape.
"""

import re
import lxml.html as htmlparser

import json
from .decipher import decipher as decode

from ...config import NINEANIME
from ...helper import construct_site_based_regex

NINEANIME_URL = NINEANIME

WAF_TOKEN = re.compile(r"(\d{64})")
WAF_SEPARATOR = re.compile(r"\w{2}")

ANIME_SLUG = construct_site_based_regex(NINEANIME, extra_regex=r'/watch/[^&?/]+\.(?P<slug>[^&?/]+)')
MP4UPLOAD_REGEX = re.compile(r"player\|(.*)\|videojs")

def get_waf_token(session):
    with session.get(NINEANIME_URL) as cloudflare_page:
        return ''.join(chr(int(c, 16)) for c in WAF_SEPARATOR.findall(WAF_TOKEN.search(cloudflare_page.text).group(1)))

def get_url_by_hash(session, _hash, access_headers):
    with session.get(NINEANIME_URL + "ajax/anime/episode", params={'id': _hash}, headers=access_headers) as ajax_server_response:
        return decode(ajax_server_response.json().get('url', ''))
    
def get_mp4upload_by_hash(session, _hash, access_headers):
    mp4upload_url = "https://www.mp4upload.com/embed-%s.html" % re.search(r"embed-(.*)\.html", get_url_by_hash(session, _hash, access_headers)).group(1)
    with session.get(mp4upload_url) as mp4upload_embed_page:
        if mp4upload_embed_page.text == 'File was deleted':
            return []
        content = MP4UPLOAD_REGEX.search(mp4upload_embed_page.text).group(1).split('|')
        return [{'quality': content[53], 'stream_url': "{3}://{18}.{1}.{0}:{73}/d/{72}/{71}.{70}".format(*content)}]

def fetcher(session, url, check):
    
    waf = get_waf_token(session)
    slug = ANIME_SLUG.search(url).group("slug")
    
    access_headers = {
        'cookie': 'waf_cv=%s' % waf,
        'referer': NINEANIME_URL,
    }
    
    with session.get(NINEANIME_URL + "ajax/anime/servers", params={'id': slug}, headers=access_headers) as ajax_server_response:
        data = htmlparser.fromstring(ajax_server_response.json().get('html', ''))
        
    for el in data.xpath('//li/a'):
        en = int(el.get('data-base', 0))
        if check(en):
            yield get_mp4upload_by_hash(session, json.loads(el.get('data-sources', '{}')).get('35', ''), access_headers), en