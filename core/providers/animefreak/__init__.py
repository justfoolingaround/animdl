import re

import lxml.html as htmlparser

from ...config import ANIMEFREAK
from ...helper import construct_site_based_regex

from functools import partial

EPISODE_RE = construct_site_based_regex(ANIMEFREAK, extra_regex=r'/watch/([^?&/]+)/episode/episode-\d+')
STREAM_URL_RE = re.compile(r"(?:https?://)?st\d+\.anime1\.com/(?P<file>.*)")

BASE_URL = ANIMEFREAK + "watch/{}"
BASE_STREAM_URL = "https://st%d.anime1.com/%s"

def send_valid(session, stream_url):

    with session.get(stream_url, stream=True, verify=False) as response:
        if response.ok:
            return stream_url
    
    file = STREAM_URL_RE.search(stream_url).group('file')
    
    for trial in range(6, 12):
        url = BASE_STREAM_URL % (trial, file)
        with session.get(url, stream=True, verify=False) as response:
            if response.ok:
                return url

def extract_stream_uri(session, episode_url):
    with session.get(episode_url) as episode_page:
        return send_valid(session, re.search(r"file\s*=\s*['\"]([^'\"]*)", episode_page.text).group(1))

def fetcher(session, url, check):
    match  = EPISODE_RE.search(url)
    if match:
        url = BASE_URL.format(match.group(1))

    with session.get(url) as anime_page:
        html_element = htmlparser.fromstring(anime_page.text)
        episodes = html_element.xpath('(//ul[@class="check-list"])[2]/li/a') or html_element.xpath('//ul[@class="check-list"]/li/a')

    for episode in reversed(episodes):
        episode_number = re.search(r"\d+", episode.text_content())
        en = int(episode_number.group(0) if episode_number else 1)
        if check(en):
            yield partial(lambda s, e: [{'quality': 'unknown', 'stream_url': extract_stream_uri(s, e.get('href')), 'headers':  {'ssl_verification': False}}], session, episode), en