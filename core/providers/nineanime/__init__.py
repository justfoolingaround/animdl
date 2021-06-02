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
SKEY_RE = re.compile(r"skey = '(?P<skey>[^']+)';")

VIDSTREAM_REGEXES = {
    'online': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?vidstreamz\.online/(?:e|embed)/(?P<id>[A-Z0-9]+)"),
        'info_ajax': 'https://vidstreamz.online/info/%s',
        },
    'pro': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?vidstream\.pro/(?:e|embed)/(?P<id>[A-Z0-9]+)"),
        'info_ajax': 'https://vidstream.pro/info/%s',
        },
}

def get_appropriate_vidstream(vidstream_url):
    for content, data in VIDSTREAM_REGEXES.items():
        match = data.get('matcher').search(vidstream_url)
        if match:
            return match.group('id'), data.get('info_ajax', ''), "https://vidstream.pro/e/%s"
    
    raise Exception("VidStream unsupported URL: '%s', please raise an issue on the GitHub with the anime name and episode immediately!" % vidstream_url)

def get_waf_token(session):
    with session.get(NINEANIME_URL) as cloudflare_page:
        return ''.join(chr(int(c, 16)) for c in WAF_SEPARATOR.findall(WAF_TOKEN.search(cloudflare_page.text).group(1)))
    
def get_vidstream_by_hash(session, hash, access_headers):
    
    with session.get(NINEANIME_URL + "ajax/anime/episode", params={'id': hash}, headers=access_headers) as ajax_server_response:
        data = decode(ajax_server_response.json().get('url', ''))
        
    vidstream_id, vidstream_info_ajax, established_data = get_appropriate_vidstream(data)
    vidstream_embed_url = established_data % vidstream_id
    
    with session.get(vidstream_embed_url, headers={'referer': NINEANIME_URL}) as vidstream_content:
        skey_match = SKEY_RE.search(vidstream_content.text)    
        if not skey_match:
            if vidstream_content.ok:
                raise Exception('Could not find session key from VidStream; associated url: "%s" (Include this in your GitHub issue!).' % vidstream_embed_url)
            return []
        
    skey = skey_match.group('skey')
    
    with session.get(vidstream_info_ajax % vidstream_id, params={'skey': skey}, headers={'referer': vidstream_embed_url}) as vidstream_info:
        return [{'quality': content.get('label', 'unknown'), 'stream_url': content.get('file', ''), 'headers': {'referer': vidstream_embed_url}} for content in vidstream_info.json().get('media', {}).get('sources', [])] 
    
    
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
            yield get_vidstream_by_hash(session, json.loads(el.get('data-sources', '{}')).get('41', ''), access_headers), en