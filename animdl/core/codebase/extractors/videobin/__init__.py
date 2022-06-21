import json

import regex

SOURCES_REGEX = regex.compile(r"sources: (\[.+?\])")


def extract(session, url, **opts):
    response = session.get(url)
    if response.status_code >= 400:
        return []

    sources = SOURCES_REGEX.search(response.text)

    if not sources:
        return []

    return [{"stream_url": stream} for stream in json.loads(sources.group(1))]
