import re

import lxml.html as htmlparser

EPISODE_RE = re.compile(r"(?:https?://)?(?:\S+\.)?animefreak\.tv/watch/([^?&/]+)/episode/episode-\d+")
STREAM_URL_RE = re.compile(r"(?:https?://)?st\d+\.anime1\.com/(?P<file>.*)")

BASE_URL = "https://www.animefreak.tv/watch/{}"
BASE_STREAM_URL = "https://st%d.anime1.com/%s"

def send_valid(session, stream_url):

    with session.get(stream_url, stream=True) as response:
        if response.ok:
            return stream_url
    
    file = STREAM_URL_RE.search(stream_url).group('file')
    
    for trial in range(6, 12):
        with session.get(url := BASE_STREAM_URL % (trial, file), stream=True) as response:
            if response.ok:
                return url

def extract_stream_uri(session, episode_url):
    with session.get(episode_url) as episode_page:
        return send_valid(session, re.search(r"file\s*=\s*['\"]([^'\"]*)", episode_page.text).group(1))

def fetcher(session, url, check):
    if match := EPISODE_RE.search(url):
        url = BASE_URL.format(match.group(1))

    with session.get(url) as anime_page:
        html_element = htmlparser.fromstring(anime_page.text)
        episodes = html_element.xpath('(//ul[@class="check-list"])[2]/li/a') or html_element.xpath('//ul[@class="check-list"]/li/a')

    session.verify = False        
    for episode in reversed(episodes):
        if check(int(re.search(r"\d+", episode.text_content()).group(0))):
            yield [{'quality': 'unknown', 'stream_url': extract_stream_uri(session, episode.get('href')), 'headers':  {'ssl_verification': False}}]
    session.verify = True