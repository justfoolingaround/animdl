import re

import lxml.html as htmlparser

EPISODE_RE = re.compile(r"(?:https?://)?(?:\S+\.)?animefreak\.tv/watch/([^?&/]+)/episode/episode-\d+")
BASE_URL = "https://www.animefreak.tv/watch/{}"

def extract_stream_uri(session, episode_url):
    with session.get(episode_url) as episode_page:
        return re.search(r"file\s*=\s*['\"]([^'\"]*)", episode_page.text).group(1)

def fetcher(session, url, check):
    if match := EPISODE_RE.search(url):
        url = BASE_URL.format(match.group(1))

    with session.get(url) as anime_page:
        html_element = htmlparser.fromstring(anime_page.text)
        episodes = html_element.xpath('(//ul[@class="check-list"])[2]/li/a') or html_element.xpath('//ul[@class="check-list"]/li/a')
        
    for episode in reversed(episodes):
        if check(int(re.search(r"\d+", episode.text_content()).group(0))):
            yield [{'quality': 'unknown', 'stream_url': extract_stream_uri(session, episode.get('href'))}]