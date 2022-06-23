from functools import partial

import lxml.html as htmlparser
import regex
import yarl

from ....config import ANIMEOUT
from ...helper import construct_site_based_regex, group_episodes, parse_from_content

REGEX = construct_site_based_regex(ANIMEOUT, extra_regex=r"/([^?&/]+)")

TITLES_REGEX = regex.compile(r'<h1 class="page-title">(.+?)</h1>')

public_domains = {
    "nimbus": "pub9",
    "chomusuke": "pub8",
    "chunchunmaru": "pub7",
    "ains": "pub6",
    "yotsuba": "pub5",
    "slaine": "pub4",
    "jibril": "pub3",
    "sv1": "pub2",
    "sv4": "pub2",
    "download": "pub1",
}


def animeout_stream_url(url: "yarl.URL") -> str:

    host_prefix, _ = url.host.split(".", 1)

    if host_prefix in public_domains:
        url = url.with_host(f"{public_domains[host_prefix]}.{_}")

    return url.human_repr()


def fetcher(session, url, check, match):
    animeout_page = session.cf_request("GET", url)
    parsed = htmlparser.fromstring(animeout_page.text)

    downloadables = (
        yarl.URL(_.get("href"))
        for _ in parsed.cssselect('.article-content a[href$="mkv"]')
        if "Download" in _.text_content()
    )

    for episode, content in sorted(
        (
            group_episodes(
                parse_from_content(
                    content,
                    name_processor=lambda c: c.name,
                    stream_url_processor=animeout_stream_url,
                )
                for content in downloadables
            ).items()
        ),
        key=lambda x: x[0],
    ):
        if check(episode):
            yield partial(list, content), episode


def metadata_fetcher(session, url, match):
    return {"titles": TITLES_REGEX.findall(session.cf_request("GET", url).text)}
