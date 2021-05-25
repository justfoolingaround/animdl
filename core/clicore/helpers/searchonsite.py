"""
All the search algorithms for all the providers available in AnimDL.
"""

import re

import lxml.html as htmlparser

FOURANIME_URL_SEARCH = "https://4anime.to/?s=%s"

NINEANIME_URL = "https://9anime.to"
NINEANIME_URL_SEARCH = "https://9anime.to/search"

ANIMEFREAK_URL_SEARCH_AJAX = "https://www.animefreak.tv/search/topSearch"
ANIMEFREAK_URL_CONTENT = "https://animefreak.tv/watch/%s"

ANIMEPAHE_URL_CONTENT = "https://animepahe.com/anime/%s"
ANIMEPAHE_URL_SEARCH_AJAX = "https://animepahe.com/api"

ANIMIX_URL_SEARCH_POST = "https://v1.zv5vxk4uogwdp7jzbh6ku.workers.dev/"
ANIMIX_URL_CONTENT = "https://animixplay.to"

GOGOANIME_URL_SEARCH = "https://www1.gogoanime.ai//search.html?"
GOGOANIME_URL = "https://www1.gogoanime.ai"

TWIST_URL_CONTENT_API = "https://api.twist.moe/api/anime"
TWIST_URL_CONTENT = "https://twist.moe/a/"

WAF_TOKEN = re.compile(r"(\d{64})")
WAF_SEPARATOR = re.compile(r"\w{2}")

def search_4anime(session, query):
    with session.get(FOURANIME_URL_SEARCH % query) as fouranime_results:
        parsed = htmlparser.fromstring(fouranime_results.text)

    for results in parsed.xpath('//div[@id="headerDIV_2"]/div[@id="headerDIV_95"]/a'):
        yield {'anime_url': results.get('href'), 'name': ' '.join(_.text_content() for _ in results.xpath('div'))}

def search_9anime(session, query):
    with session.get(NINEANIME_URL) as cloudflare_page:
        waf_token =  ''.join(chr(int(c, 16)) for c in WAF_SEPARATOR.findall(WAF_TOKEN.search(cloudflare_page.text).group(1)))
    
    with session.get(NINEANIME_URL_SEARCH, params={'keyword': query}, headers={'cookie': 'waf_cv=%s' % waf_token}) as nineanime_results:
        parsed = htmlparser.fromstring(nineanime_results.text)
    
    for results in parsed.xpath('//ul[@class="anime-list"]/li/a[@class="name"]'):
        yield {'anime_url': NINEANIME_URL + results.get('href'), 'name': results.get('data-jtitle')}

def search_animefreak(session, query):
    with session.get(ANIMEFREAK_URL_SEARCH_AJAX, params={'q': query}) as animefreak_results:
        content = animefreak_results.json()
        
    for results in content.get('data', []):
        yield {'anime_url': ANIMEFREAK_URL_CONTENT % results.get('seo_name', ''), 'name': results.get('name')}

def search_animepahe(session, query):
    with session.get(ANIMEPAHE_URL_SEARCH_AJAX, params={'q': query, 'm': 'search'}) as animepahe_results:
        content = animepahe_results.json()
        
    for results in content.get('data'):
        yield {'anime_url': ANIMEPAHE_URL_CONTENT % results.get('session'), 'name': results.get('title')}

def search_animixplay(session, query):
    with session.post(ANIMIX_URL_SEARCH_POST, data={'q2': query, 'origin': '1', 'root': 'animixplay.to'}) as animix_results:
        content = htmlparser.fromstring(animix_results.json().get('result'))

    for results in content.xpath('//p[@class="name"]/a'):
        yield {'anime_url': ANIMIX_URL_CONTENT + results.get('href'), 'name': results.get('title')}

def search_gogoanime(session, query):
    with session.get(GOGOANIME_URL_SEARCH, params={'keyword': query}) as gogoanime_results:
        parsed = htmlparser.fromstring(gogoanime_results.text)
        
    for results in parsed.xpath('//p[@class="name"]/a'):
        yield {'anime_url': GOGOANIME_URL + results.get('href'), 'name': results.get('title')}

def search_twist(session, query):
    with session.get(TWIST_URL_CONTENT_API, headers={'x-access-token': '0df14814b9e590a1f26d3071a4ed7974'}) as content:
        animes = content.json()
        
    searcher = lambda q, content: any([q.lower() in (content.get('title') or '').lower(), q.lower() in (content.get('alt_title') or '').lower(), q.lower() in (content.get('slug', {}).get('slug') or '').lower(),])

    for anime in animes:
        if searcher(query, anime):
            yield {'anime_url': TWIST_URL_CONTENT + anime.get('slug', {}).get('slug'), 'name': anime.get('title', '')}

link = {
    '4anime': search_4anime,
    '9anime': search_9anime,
    'animefreak': search_animefreak,
    'animepahe': search_animepahe,
    'animixplay': search_animixplay,
    'gogoanime': search_gogoanime,
    'twist': search_twist,
}

get_searcher = link.get