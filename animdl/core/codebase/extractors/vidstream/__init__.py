import regex


EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:e(?:mbed)?)/([a-zA-Z0-9]+)")


def extract(session, url, **opts):

    match = EMBED_URL_REGEX.search(url)
    host, slug = match.group(1, 2)

    vidstream_info = session.get(
        "{}info/{}".format(host, slug), headers={"referer": url}, params={"d": "kr"}
    )

    if vidstream_info.status_code == 404:
        return []

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json().get("media", {}).get("sources", [])
    ]
