from functools import lru_cache, partial

import regex

from ....config import ANIMEPAHE
from ...helper import construct_site_based_regex

REGEX = construct_site_based_regex(ANIMEPAHE, extra_regex=r"/(?:anime|play)/([^?&/]+)")


API_URL = ANIMEPAHE + "api"
SITE_URL = ANIMEPAHE

PLAYER_RE = construct_site_based_regex(ANIMEPAHE, extra_regex=r"/play/([^?&/]+)")
ID_RE = regex.compile(r'let id = "(.+?)"')
KWIK_RE = regex.compile(r"Plyr\|(.+?)'")

TITLES_REGEX = regex.compile(r"<h1>(.+?)</h1>")


@lru_cache()
def get_session_page(session, page, release_id):
    return session.get(
        API_URL,
        params={"m": "release", "id": release_id, "sort": "episode_desc", "page": page},
    ).json()


def get_streams_from_embed_url(session, embed_uri):
    embed_page = session.get(embed_uri, headers={"referer": ANIMEPAHE}).text
    return "{}://{}-{}.{}.{}.{}/{}/{}/{}/{}.{}".format(
        *KWIK_RE.search(embed_page).group(1).split("|")[::-1]
    )


def get_stream_url(session, release_id, stream_session):

    stream_url_data = session.get(
        API_URL,
        params={"m": "links", "id": release_id, "session": stream_session, "p": "kwik"},
    )
    content = stream_url_data.json().get("data", [])

    for d in content:
        for quality, data in d.items():

            yield {
                "quality": quality,
                "headers": {"referer": data.get("kwik")},
                "stream_url": get_streams_from_embed_url(session, data.get("kwik")),
            }


def get_stream_urls_from_page(session, release_id, page, check):
    data = get_session_page(session, page, release_id).get("data")
    for content in reversed(data):
        if check(content.get("episode", 0)):
            yield partial(
                lambda session, release_id, content: (
                    [*get_stream_url(session, release_id, content.get("session"))]
                ),
                session,
                release_id,
                content,
            ), content.get("episode", 0)


def predict_pages(total, check):
    """
    A calculative function to minimize API calls.
    """
    for x in range(1, total + 1):
        if check(x):
            yield (total - x) // 30 + 1


def page_minimization(page_generator):
    return sorted(list(dict.fromkeys(page_generator)), reverse=True)


def bypass_ddos_guard(session):
    js_bypass_uri = regex.search(
        r"'(.*?)'", session.get("https://check.ddos-guard.net/check.js").text
    ).group(1)
    session.cookies.update(session.get(ANIMEPAHE + js_bypass_uri).cookies)


def fetcher(session, url, check, match):
    player_match = PLAYER_RE.search(url)

    if player_match:
        url = "https://www.animepahe.com/anime/%s" % player_match.group(1)

    anime_page = session.get(url)
    release_id = ID_RE.search(anime_page.text).group(1)

    fpd = get_session_page(session, "1", release_id)

    if fpd.get("last_page") == 1:
        yield from get_stream_urls_from_page(session, release_id, "1", check)
        return

    for page in page_minimization(predict_pages(fpd.get("total"), check)):
        yield from get_stream_urls_from_page(session, release_id, page, check)


def metadata_fetcher(session, url, match):
    player_match = PLAYER_RE.search(url)

    if player_match:
        url = "https://www.animepahe.com/anime/%s" % player_match.group(1)

    return {
        "titles": TITLES_REGEX.findall(session.get(url).text),
    }
