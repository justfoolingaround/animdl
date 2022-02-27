import regex


EMBED_URL_REGEX = regex.compile(r"(.+?/)(?:e(?:mbed)?)/([a-zA-Z0-9]+)")
SKEY_RE = regex.compile(r"window\.skey = '(.+?)'")


def extract(session, url, **opts):

    params = {}

    match = EMBED_URL_REGEX.search(url)
    host, slug = match.group(1, 2)

    if host == "https://mcloud.to/":
        params.update(
            skey=SKEY_RE.search(
                session.get(url, headers=opts.get("headers", {})).text
            ).group(1)
        )

    vidstream_info = session.get(
        "{}info/{}".format(host, slug), headers={"referer": url}, params=params
    )

    if vidstream_info.status_code == 404:
        return []

    return [
        {"stream_url": content.get("file", ""), "headers": {"referer": url}}
        for content in vidstream_info.json().get("media", {}).get("sources", [])
    ]
