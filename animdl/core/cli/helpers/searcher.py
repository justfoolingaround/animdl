"""
All the search algorithms for all the providers available in AnimDL.
"""

import json

import lxml.html as htmlparser

from ...config import *
from .fuzzysearch import search

NINEANIME_URL_SEARCH = NINEANIME + "search"

ANIMEPAHE_URL_CONTENT = ANIMEPAHE + "anime/%s"
ANIMEPAHE_URL_SEARCH_AJAX = ANIMEPAHE + "api"

ANIMEOUT_URL_SEARCH_AJAX = ANIMEOUT + "wp-admin/admin-ajax.php"

ANIMIX_URL_SEARCH_API = "https://cdn.animixplay.to/api/search"

ANIMIX_URL_SEARCH_POST = "https://v1.zv5vxk4uogwdp7jzbh6ku.workers.dev/"
ANIMIX_URL_CONTENT = ANIMIXPLAY.rstrip('/')

GOGOANIME_URL_SEARCH = GOGOANIME + "/search.html?"

TENSHI_URL_SEARCH_POST = TENSHI + "anime/search"
HAHO_URL_SEARCH_POST = HAHO + "anime/search"

TWIST_URL_CONTENT_API = "https://api.twist.moe/api/anime"
TWIST_URL_CONTENT = TWIST + "a/"

def placeholder(session, query):
    yield from []

def search_9anime(session, query):
    nineanime_results = session.get(
        NINEANIME_URL_SEARCH,
        params={
            'keyword': query})
    parsed = htmlparser.fromstring(nineanime_results.text)
    for results in parsed.xpath(
            '//ul[@class="anime-list"]/li/a[@class="name"]'):
        yield {'anime_url': NINEANIME.rstrip('/') + results.get('href'), 'name': results.text_content()}

def search_animekaizoku(session, query):
    animekaizoku_results = htmlparser.fromstring(session.get(
        ANIMEKAIZOKU,
        params={'s': query}
    ).text)
    for results in animekaizoku_results.cssselect('.post-title'):
        yield {'anime_url': ANIMEKAIZOKU + results.cssselect('a')[0].get('href'), 'name': results.text_content()}

def search_allanime(session, query):

    gql_response = session.get(ALLANIME + 'graphql', params={'variables': '{"search":{"allowAdult":true,"query":"%s"},"translationType":"sub"}' % query.replace('"', '\\"'), 'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"9343797cc3d9e3f444e2d3b7db9a84d759b816a4d84512ea72d079f85bb96e98"}}'})

    for result in gql_response.json().get('data', {}).get('shows', {}).get('edges', []):
        if any(a for k, a in result.get('availableEpisodes', {}).items()):
            yield {'anime_url': ALLANIME + "anime/{[_id]}".format(result), 'name': result.get('name')}

def search_animepahe(session, query):
    
    animepahe_results = session.get(
        ANIMEPAHE_URL_SEARCH_AJAX, params={
            'q': query, 'm': 'search'})
    content = animepahe_results.json()

    for results in content.get('data', []):
        yield {'anime_url': ANIMEPAHE_URL_CONTENT % results.get('session'), 'name': results.get('title')}


def search_animeout(session, query):
    animeout_results = session.get(ANIMEOUT, params={'s': query})
    content = htmlparser.fromstring(animeout_results.text)

    for result in content.xpath('//h3[@class="post-title entry-title"]/a'):
        yield {'anime_url': result.get('href'), 'name': result.text_content()}


def search_animixplay(session, query):
    parsed = htmlparser.fromstring(
        session.post(
            'https://cachecow.eu/api/search', data={
                'qfast': query}).json().get('result') or "<div></div>")

    for results in parsed.cssselect('.name > a'):
        yield {'anime_url': ANIMIXPLAY[:-1] + results.get('href'), 'name': results.get('title')}


def search_gogoanime(session, query):
    parsed = htmlparser.fromstring(
        session.get(
            GOGOANIME_URL_SEARCH, params={
                'keyword': query}).text)

    for results in parsed.xpath('//p[@class="name"]/a'):
        yield {'anime_url': GOGOANIME.strip('/') + results.get('href'), 'name': results.get('title')}

def search_kawaiifu(session, query):
    for results in htmlparser.fromstring(session.get(KAWAIIFU + "search-movie", params={'keyword': query}).text).cssselect('.info > h4 > a:last-child'):
        yield {'anime_url': results.get('href'), 'name': results.text_content().strip()}

def search_twist(session, query):
    content = session.get(
        TWIST_URL_CONTENT_API, headers={
            'x-access-token': '0df14814b9e590a1f26d3071a4ed7974'})
    animes = content.json()

    for match, anime in search(query, animes, processor=lambda r: r.get(
            'title') or r.get('alt_title')):
        yield {'anime_url': TWIST_URL_CONTENT + anime.get('slug', {}).get('slug'), 'name': anime.get('title', '')}


def search_crunchyroll(session, query):
    content = json.loads(
        session.get(
            CRUNCHYROLL +
            "ajax/?req=RpcApiSearch_GetSearchCandidates").text.strip('*/\n -secur'))

    for match, anime in search(query, content.get(
            'data', []), processor=lambda r: r.get('name')):
        yield {'anime_url': anime.get('link', '').strip('/'), 'name': anime.get('name', '')}

def search_nyaasi(session, query):
    for anime in htmlparser.fromstring(session.get(NYAASI, params={'q': query, 's': 'seeders', 'o': 'desc'}).text).cssselect('tr > td[colspan="2"] > a[title]:last-child	'):
        yield {'anime_url': NYAASI + anime.get('href')[1:], 'name': anime.get('title', '').strip()}


def search_tenshi(session, query):
    tenshi_page = session.get(TENSHI)
    session_id = tenshi_page.cookies.get('tenshimoe_session')
    token = htmlparser.fromstring(tenshi_page.text).xpath(
        '//meta[@name="csrf-token"]')[0].get('content')

    ajax_content = session.post(
        TENSHI_URL_SEARCH_POST,
        data={
            'q': query},
        headers={
            'x-requested-with': 'XMLHttpRequest',
            'x-csrf-token': token,
            'referer': 'https://tenshi.moe/',
            'cookie': 'tenshimoe_session={}'.format(session_id)})
    results = ajax_content.json()

    for result in results:
        yield {'name': result.get('title'), 'anime_url': result.get('url')}

def search_zoro(session, query):
    for result in htmlparser.fromstring(session.get(ZORO + "/search", params={'keyword': query}).text).cssselect('a.item-qtip[title][data-id]'):
        yield {
            'name': result.get('title'),
            'anime_url': ZORO + result.get('href')[1:-11]
        }


def search_haho(session, query):

    haho_page = session.get(HAHO)
    session_id = haho_page.cookies.get('hentai_aho_streaming_session')
    token = htmlparser.fromstring(haho_page.text).xpath(
        '//meta[@name="csrf-token"]')[0].get('content')

    ajax_content = session.post(
        HAHO_URL_SEARCH_POST,
        data={
            'q': query},
        headers={
            'x-requested-with': 'XMLHttpRequest',
            'x-csrf-token': token,
            'referer': 'https://haho.moe/',
            'cookie': 'hentai_aho_streaming_session={}'.format(session_id)})
    results = ajax_content.json()

    for result in results:
        yield {'name': result.get('title'), 'anime_url': result.get('url')}

link = {
    '9anime': search_9anime,
    'animekaizoku': search_animekaizoku,
    'allanime': search_allanime,
    'animepahe': search_animepahe,
    'animeout': search_animeout,
    'animixplay': search_animixplay,
    'crunchyroll': search_crunchyroll,
    'kawaiifu': search_kawaiifu,
    'gogoanime': search_gogoanime,
    'haho': search_haho,
    'tenshi': search_tenshi,
    'nyaa': search_nyaasi,
    'twist': search_twist,
    'zoro': search_zoro,
}

def get_searcher(provider):
    searcher = link.get(provider)
    if searcher:
        searcher.provider = provider
        return searcher
