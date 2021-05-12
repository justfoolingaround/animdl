import re

import lxml.html as htmlparser

EPISODE_RE = re.compile(r"(?:https?://)?(?:\S+\.)?4anime\.to/([^?&/]+)-episode-\d+")
BASE_URL = "https://4anime.to/anime/{}"

def extract_stream_uri(session, episode_url):
    with session.get(episode_url) as episode_page:
        return (htmlparser.fromstring(episode_page.text).xpath('//video[@id="example_video_1"]/source') or [{}])[0].get('src', 'https://4anime.to/404')

def fetcher(session, url, check):
    
    if match := EPISODE_RE.search(url):
        url = BASE_URL.format(match.group(1))
    
    with session.get(url) as anime_page:
        episodes = htmlparser.fromstring(anime_page.text).xpath('//ul[@class="episodes range active"]/li/a') # type: list[htmlparser.HtmlElement]
    
    for episode in episodes:
        if check(int(episode.text_content())):
            yield [{'quality': 'unknown', 'stream_url': extract_stream_uri(session, episode.get('href'))}]