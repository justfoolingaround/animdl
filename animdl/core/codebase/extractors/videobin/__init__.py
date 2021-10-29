import regex
import json

SOURCES_REGEX = regex.compile("sources: (\[.+?\])")

def extract(session, url, **opts):
    response = session.get(url)
    if response.status_code >= 400:
        return []

    return [{"stream_url": stream} for stream in json.loads(SOURCES_REGEX.search(response.text).group(1))]
