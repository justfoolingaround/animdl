from functools import partial

import lxml.html as htmlparser

from ....config import ANIMEONSEN
from ...helpers import construct_site_based_regex

REGEX = construct_site_based_regex(
    ANIMEONSEN,
    extra_regex=r"/(?:details/(?P<slug>[^?&/]+)|watch/(?P<watch_slug>[^?&/]+))",
)

API_ENDPOINT = "https://api.animeonsen.xyz/v4/"

AUTHENTICATION = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpcCI6IjI3LjM0LjY4LjEzOCIsImlhdCI6MTY0ODU1NTU4MiwiZXhwIjoxNjQ5MTYwMzgyLCJpc3MiOiJhbmltZW9uc2VuLWFwcCJ9.ZUy2zv_aRFtT_iqjEGtp5HO9EnkH71pM0TpcBQ0JcwU"


def get_stream_url(session, episode, slug):

    response = session.get(
        API_ENDPOINT + "content/{}/video/{}".format(slug, episode),
        headers={"Authorization": AUTHENTICATION},
    ).json()

    metadata = response.get("metadata", {})
    current, _, episodes = metadata.get("episode", [0, {}, {}])

    episode_title = episodes.get(str(current), {}).get(
        "contentTitle_episode_en"
    ) or episodes.get(str(current), {}).get("contentTitle_episode_jp", "")
    title = "Episode {}".format(current)

    if episode_title:
        title = "{}: {}".format(title, episode_title)

    streams = response.get("uri", {})

    return [
        {
            "stream_url": streams.get("stream"),
            "subtitles": list(streams.get("subtitles", {}).values()),
            "title": title,
            "headers": {
                "referer": ANIMEONSEN,
            },
        }
    ]


def fetcher(session, url, check, match):

    slug = match.group("slug") or match.group("watch_slug")

    for link in htmlparser.fromstring(
        session.get(ANIMEONSEN + "details/" + slug).text
    ).cssselect("div.episode-list > a"):
        episode_element = link.cssselect("div.episode")[0]

        episode = int(episode_element.get("data-episode", 0))

        if check(episode):
            yield partial(get_stream_url, session, episode, slug), episode


def metadata_fetcher(session, url, match):

    slug = match.group("slug") or match.group("watch_slug")

    response = session.get(
        API_ENDPOINT + "content/{}/extensive".format(slug),
        headers={"Authorization": AUTHENTICATION},
    ).json()

    titles = []

    if "content_title" in response:
        titles.append(response["content_title"])

    if "content_title_en" in response:
        titles.append(response["content_title_en"])

    return {"titles": titles}
