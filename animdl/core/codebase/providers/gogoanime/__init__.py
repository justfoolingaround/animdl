import re
from functools import partial

import lxml.html as htmlparser

from ....config import GOGOANIME
from ...helper import construct_site_based_regex

ANIME_RE = construct_site_based_regex(
    GOGOANIME, extra_regex=r"/([^&?/]+)-episode-\d+")

EPISODE_LOAD_AJAX = "https://ajax.gogo-load.com/ajax/load-list-episode"
SITE_URL = GOGOANIME


def get_episode_list(session, anime_id):
    """
    Fetch all the episodes' url from GogoAnime using.
    """
    episode_page = session.get(EPISODE_LOAD_AJAX, params={'ep_start': '0', 'ep_end': '2000', 'id': anime_id, })
    content = htmlparser.fromstring(episode_page.text)

    for episode in content.xpath('//ul[@id="episode_related"]/li/a'):
        yield SITE_URL + episode.get('href', '').strip()


def get_anime_id(html_content):
    content = html_content.xpath('//input[@id="movie_id"]')
    assert content, "No GGA Anime ID found."
    return int(content[0].get('value', 0))


def convert_to_anime_page(url):
    match = ANIME_RE.search(url)
    if match:
        return SITE_URL + "/category/%s" % match.group(1)
    return url

def get_quality(url_text):
    match = re.search(r'(\d+)P', url_text)
    if not match:
        return None
    return int(match.group(1))

def get_stream_url(session, episode_page_url):

    response = session.get(episode_page_url)
    content_parsed = htmlparser.fromstring(response.text)

    streaming = content_parsed.xpath(
        '//div[@class="play-video"]/iframe')[0].get('src')

    response = session.get('https:%s' % streaming.replace('streaming.php', 'download'), headers={'referer': "https:{}".format(streaming)})
    content = htmlparser.fromstring(response.text)

    return [{'quality': get_quality(url.text_content()), 'stream_url': url.get('href'), 'headers': {'referer': str(response.url)}} for url in content.xpath(
        '//div[@class="dowload"]/a[@download]')]


def fetcher(session, url, check):
    url = convert_to_anime_page(url)

    anime_page = session.get(url)
    content_id = get_anime_id(htmlparser.fromstring(anime_page.text))

    episodes = reversed([*get_episode_list(session, content_id)])

    for index, episode in enumerate(episodes, 1):
        if check(index):
            yield partial(get_stream_url, session, episode), index
