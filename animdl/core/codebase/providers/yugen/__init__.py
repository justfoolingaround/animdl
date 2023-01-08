import base64
from functools import partial

from ....config import YUGEN
from ...helpers import construct_site_based_regex, optopt, superscrapers

REGEX = construct_site_based_regex(
    YUGEN, extra_regex=r"/(?:watch|anime)/(?P<anime_path>(?P<anime_id>.+?)/.+?)(?:/|$)"
)


EPISODE_REGEX = optopt.regexlib.compile(
    r'<div class="ap-.+?">Episodes</div><span class="description" .+?>(\d+)</span></div>'
)
EPISODE_TITLE_REGEX = optopt.regexlib.compile(r'<h1 class="p-10-t">\n(.+?)\n</h1>')


def iter_streams(session, anime_id, episode_id):

    data = (
        session.post(
            YUGEN + "api/embed/",
            data={
                "id": base64.b64encode(f"{anime_id}|{episode_id}".encode()).decode(),
                "ac": "0",
            },
            headers={
                "x-requested-with": "XMLHttpRequest",
            },
        )
        .json()
        .get("hls", [])
    )

    for source in data:
        url = superscrapers.yarl.URL(source)

        yield from superscrapers.iter_unpacked_from_packed_hls(session, url)


def fetcher(session, url, check, match):

    anime_page = YUGEN + "anime/" + match.group("anime_path")
    anime_page_html = session.get(anime_page).text
    subbed_episode_count = int(EPISODE_REGEX.search(anime_page_html).group(1))

    for episode in range(1, subbed_episode_count + 1):

        if check(episode):

            yield partial(
                lambda anime_id, episode_id: list(
                    iter_streams(session, anime_id, episode_id)
                ),
                anime_id=match.group("anime_id"),
                episode_id=episode,
            ), episode


def metadata_fetcher(session, url, match):
    anime_page = YUGEN + "anime/" + match.group("anime_path")
    anime_page_html = session.get(anime_page).text

    return {
        "titles": [EPISODE_TITLE_REGEX.search(anime_page_html).group(1)],
    }
