from functools import partial
import json
import re

import lxml.html as htmlparser

from ....config import CRUNCHYROLL
from ...helper import construct_site_based_regex

from .geobypass import geobypass_response

CRUNCHYROLL_REGEX = construct_site_based_regex(
    CRUNCHYROLL, extra_regex=r'/([^?/&]+)')

CONTENT_METADATA = re.compile(r"vilos\.config\.media = (\{.+\})")


def get_subtitle(subtitles, lang='enUS'):
    for sub in subtitles:
        if sub.get('language') == lang:
            yield sub.get('url')


def get_stream_url(session, episode_page):
    json_content = json.loads(CONTENT_METADATA.search(
        geobypass_response(episode_page).text).group(1))
    metadata = json_content.get('metadata')

    for stream in json_content.get('streams'):
        if stream.get('format') in ['adaptive_dash', 'adaptive_hls', 'multitrack_adaptive_hls_v2',
                                    'vo_adaptive_dash', 'vo_adaptive_hls'] and stream.get('hardsub_lang') in [None, 'enUS']:
            yield_content = {
                'stream_url': stream.get('url'),
                'title': metadata.get('title')}

            if stream.get('hardsub_lang') is None:
                yield_content.update(
                    {'subtitle': [*get_subtitle(json_content.get('subtitles'))], 'download': False})

            yield yield_content


def fetcher(session, url, check):

    url = CRUNCHYROLL + \
        CRUNCHYROLL_REGEX.search(url).group(1)

    episode_pages = htmlparser.fromstring(
        geobypass_response(url).text).cssselect('.episode')[::-1]

    for episode in episode_pages:
        episode_number = 0
        match = re.search(
            r'Episode (\d+)',
            episode.xpath('span')[0].text_content())
        if match:
            episode_number = int(match.group(1))
        if check(episode_number):
            yield partial(lambda s, h: [*get_stream_url(s, CRUNCHYROLL + h.strip('/'))], session, episode.get('href')), episode_number
