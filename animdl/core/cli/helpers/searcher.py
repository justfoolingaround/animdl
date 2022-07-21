"""
All the search algorithms for all the providers available in AnimDL.
"""

import json

import lxml.html as htmlparser

from ...codebase.helper import uwu
from ...config import *
from .fuzzysearch import search

NINEANIME_URL_SEARCH = NINEANIME + "filter"

ANIMEPAHE_URL_CONTENT = ANIMEPAHE + "anime/%s"
ANIMEPAHE_URL_SEARCH_AJAX = ANIMEPAHE + "api"

ANIMEOUT_URL_SEARCH_AJAX = ANIMEOUT + "wp-admin/admin-ajax.php"

ANIMIX_URL_SEARCH_API = "https://cdn.animixplay.to/api/search"

ANIMIX_URL_SEARCH_POST = "https://v1.zv5vxk4uogwdp7jzbh6ku.workers.dev/"
ANIMIX_URL_CONTENT = ANIMIXPLAY.rstrip("/")

GOGOANIME_URL_SEARCH = GOGOANIME + "/search.html?"

TENSHI_URL_SEARCH_POST = TENSHI + "anime/search"
HAHO_URL_SEARCH_POST = HAHO + "anime/search"

TWIST_URL_CONTENT_API = "https://api.twist.moe/api/anime"
TWIST_URL_CONTENT = TWIST + "a/"


def placeholder(session, query):
    yield from []


def search_9anime(session, query):
    nineanime_results = session.get(
        NINEANIME_URL_SEARCH, params={"keyword": query, "sort": "views:desc"}
    )
    parsed = htmlparser.fromstring(nineanime_results.text)
    for results in parsed.cssselect(".anime-list .name"):
        yield {
            "anime_url": NINEANIME.rstrip("/") + results.get("href"),
            "name": results.text_content(),
        }


def search_animekaizoku(session, query):
    animekaizoku_results = htmlparser.fromstring(
        session.get(ANIMEKAIZOKU, params={"s": query}).text
    )
    for results in animekaizoku_results.cssselect(".post-title"):
        yield {
            "anime_url": ANIMEKAIZOKU + results.cssselect("a")[0].get("href"),
            "name": results.text_content(),
        }


def search_allanime(session, query):

    gql_response = session.get(
        ALLANIME + "graphql",
        params={
            "variables": '{"search":{"allowAdult":true,"query":"%s"},"translationType":"sub"}'
            % query.replace('"', '\\"'),
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"9343797cc3d9e3f444e2d3b7db9a84d759b816a4d84512ea72d079f85bb96e98"}}',
        },
    )

    for result in gql_response.json().get("data", {}).get("shows", {}).get("edges", []):
        if any(a for k, a in result.get("availableEpisodes", {}).items()):
            yield {
                "anime_url": ALLANIME + "anime/{[_id]}".format(result),
                "name": result.get("name"),
            }


def search_animepahe(session, query):

    animepahe_results = session.get(
        ANIMEPAHE_URL_SEARCH_AJAX, params={"q": query, "m": "search"}
    )
    content = animepahe_results.json()

    for results in content.get("data", []):
        yield {
            "anime_url": ANIMEPAHE_URL_CONTENT % results.get("session"),
            "name": results.get("title"),
        }


def search_animeout(session, query):
    animeout_results = session.cf_request("GET", ANIMEOUT, params={"s": query})
    content = htmlparser.fromstring(animeout_results.text)

    for result in content.xpath('//h3[@class="post-title entry-title"]/a'):
        yield {"anime_url": result.get("href"), "name": result.text_content()}


def search_animixplay(session, query):
    parsed = htmlparser.fromstring(
        session.post("https://cachecow.eu/api/search", data={"qfast": query}).json()[
            "result"
        ]
        or "<div></div>"
    )

    for results in parsed.cssselect("a[title]"):
        yield {
            "anime_url": ANIMIXPLAY[:-1] + results.get("href"),
            "name": results.get("title"),
        }


def search_gogoanime(session, query):
    parsed = htmlparser.fromstring(
        session.get(GOGOANIME_URL_SEARCH, params={"keyword": query}).text
    )

    for results in parsed.xpath('//p[@class="name"]/a'):
        yield {
            "anime_url": GOGOANIME.strip("/") + results.get("href"),
            "name": results.get("title"),
        }


def search_kawaiifu(session, query):
    for results in htmlparser.fromstring(
        session.get(KAWAIIFU + "search-movie", params={"keyword": query}).text
    ).cssselect(".info > h4 > a:last-child"):
        yield {"anime_url": results.get("href"), "name": results.text_content().strip()}


def search_twist(session, query):
    content = session.get(
        TWIST_URL_CONTENT_API,
        headers={"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"},
    )
    animes = content.json()

    for anime in search(
        query, animes, processor=lambda r: r.get("title") or r.get("alt_title")
    ):
        yield {
            "anime_url": TWIST_URL_CONTENT + anime.get("slug", {}).get("slug"),
            "name": anime.get("title", ""),
        }


def search_crunchyroll(session, query, *, scheme="http"):
    content = json.loads(
        session.get(
            CRUNCHYROLL + "ajax/?req=RpcApiSearch_GetSearchCandidates",
            headers={
                "Referer": "https://www.google.com/",
            },
        ).text.strip("*/\n -secur")
    )

    for anime in search(
        query, content.get("data", []), processor=lambda r: r.get("name")
    ):
        yield {
            "anime_url": scheme + anime.get("link", "").strip("/")[5:],
            "name": anime.get("name", ""),
        }


def search_nyaasi(session, query):
    for anime in htmlparser.fromstring(
        session.get(NYAASI, params={"q": query, "s": "seeders", "o": "desc"}).text
    ).cssselect('tr > td[colspan="2"] > a[title]:last-child	'):
        yield {
            "anime_url": NYAASI + anime.get("href")[1:],
            "name": anime.get("title", "").strip(),
        }


def search_tenshi(session, query, *, domain=TENSHI):
    uwu.bypass_ddos_guard(session, domain)
    tenshi_page = htmlparser.fromstring(
        session.get(domain + "anime", params={"q": query}).text
    )

    for result in tenshi_page.cssselect(".list > li > a"):
        yield {"name": result.get("title"), "anime_url": result.get("href")}


def search_zoro(session, query):
    for result in htmlparser.fromstring(
        session.get(ZORO + "/search", params={"keyword": query}).text
    ).cssselect("a.item-qtip[title][data-id]"):
        yield {
            "name": result.get("title"),
            "anime_url": ZORO + result.get("href")[1:-11],
        }


def search_h_ntai_stream(session, query):
    for result in htmlparser.fromstring(
        session.get(HENTAISTREAM, params={"s": query}).text
    ).cssselect("article > .bsx > a"):
        yield {
            "name": result.get("title"),
            "anime_url": result.get("href"),
        }


def search_haho(session, query):
    yield from search_tenshi(session, query, domain=HAHO)


provider_searcher_mapping = {
    "9anime": search_9anime,
    "animekaizoku": search_animekaizoku,
    "allanime": search_allanime,
    "animepahe": search_animepahe,
    "animeout": search_animeout,
    "animixplay": search_animixplay,
    "crunchyroll": search_crunchyroll,
    "kamyroll": lambda *args, **kwargs: search_crunchyroll(
        *args, **kwargs, scheme="kamyroll"
    ),
    "kawaiifu": search_kawaiifu,
    "gogoanime": search_gogoanime,
    "haho": search_haho,
    "hentaistream": search_h_ntai_stream,
    "tenshi": search_tenshi,
    "nyaa": search_nyaasi,
    "twist": search_twist,
    "zoro": search_zoro,
}
