"""
All the search algorithms for all the providers available in AnimDL.
"""

from urllib.parse import unquote

import lxml.html as htmlparser

from animdl.core.codebase.providers.allanime import gql_api as allanime_gql_api
from animdl.utils.powertools import ctx

from ...codebase.helpers import uwu
from ...codebase.providers.kamyroll.api import get_api
from ...config import (
    ALLANIME,
    ANIMEKAIZOKU,
    ANIMEOUT,
    ANIMEPAHE,
    ANIMIXPLAY,
    GOGOANIME,
    HAHO,
    HENTAISTREAM,
    KAWAIIFU,
    MARIN,
    NINEANIME,
    TWIST,
    YUGEN,
    ZORO,
)
from .fuzzysearch import search


def search_9anime(session, query):
    nineanime_results = session.get(NINEANIME + "filter", params={"keyword": query})

    parsed = htmlparser.fromstring(nineanime_results.text)
    for results in parsed.cssselect("a.name"):
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

    for result in allanime_gql_api.api.iter_search_results(session, query):
        yield {
            "anime_url": ALLANIME + f"anime/{result['_id']}",
            "name": result["name"],
        }


def search_animepahe(session, query):

    animepahe_results = session.get(
        ANIMEPAHE + "api", params={"q": query, "m": "search"}
    )
    content = animepahe_results.json()

    for results in content.get("data", []):
        yield {
            "anime_url": ANIMEPAHE + "anime/" + results.get("session"),
            "name": results.get("title"),
        }


def search_animeout(session, query):
    animeout_results = session.cf_request(session, "GET", ANIMEOUT, params={"s": query})
    content = htmlparser.fromstring(animeout_results.text)

    for result in content.xpath('//h3[@class="post-title entry-title"]/a'):
        yield {"anime_url": result.get("href"), "name": result.text_content()}


def search_animixplay(session, query):
    animixplay_library = (
        _ for _ in session.get(ANIMIXPLAY + "assets/s/all.json").json() if _["e"] == "1"
    )

    for result in search(query, animixplay_library, processor=lambda r: r.get("title")):
        yield {
            "anime_url": ANIMIXPLAY + "v1/" + result.get("id"),
            "name": result.get("title"),
        }


def search_gogoanime(session, query):
    parsed = htmlparser.fromstring(
        session.get(GOGOANIME + "/search.html", params={"keyword": query}).text
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
        "https://api.twist.moe/api/anime",
        headers={"x-access-token": "0df14814b9e590a1f26d3071a4ed7974"},
    )
    animes = content.json()

    for anime in search(
        query, animes, processor=lambda r: r.get("title") or r.get("alt_title")
    ):
        yield {
            "anime_url": TWIST + "a/" + anime.get("slug", {}).get("slug"),
            "name": anime.get("title", ""),
        }


def search_crunchyroll(session, query, *, scheme="http"):
    # ajax/?req=RpcApiSearch_GetSearchCandidates

    kamyroll = get_api(session)
    for anime in kamyroll.iter_search_results(query):
        yield {
            "anime_url": f"{scheme}://www.crunchyroll.com/{anime['type']}/{anime['media_id']}",
            "name": anime["title"],
        }


def search_marin(session, query, *, domain=MARIN):

    session.get(domain, headers={"range": "bytes=0-0"})

    response = session.post(
        domain + "anime",
        json={
            "search": query,
        },
        headers={
            "x-xsrf-token": unquote(session.cookies.get("XSRF-TOKEN")),
            "x-inertia": "true",
        },
    )

    ctx.update(marin_inertia_version=response.json().get("version"))

    for result in (
        response.json().get("props", {}).get("anime_list", {}).get("data", [])
    ):
        yield {
            "name": result.get("title"),
            "anime_url": domain + "anime/" + result.get("slug"),
        }


def search_yugen(session, query):
    for result in search(
        query,
        htmlparser.fromstring(
            session.get(YUGEN + "discover/", params={"dq": query}).text
        ).cssselect("a.anime-meta[href][title]"),
        processor=lambda r: r.get("title"),
    ):
        yield {
            "name": result.get("title"),
            "anime_url": YUGEN + result.get("href")[1:],
        }


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
        session.get(HENTAISTREAM + "search/", params={"s": query}).text
    ).cssselect("article > .bsx > a"):
        yield {
            "name": result.get("title") or result.get("oldtitle"),
            "anime_url": HENTAISTREAM + result.get("href")[1:],
        }


def search_haho(session, query):
    tenshi_page = htmlparser.fromstring(
        session.get(HAHO + "anime", params={"q": query}).text
    )

    for result in tenshi_page.cssselect(".list > li > a"):
        yield {"name": result.get("title"), "anime_url": result.get("href")}


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
    "marin": search_marin,
    "twist": search_twist,
    "yugen": search_yugen,
    "zoro": search_zoro,
}
