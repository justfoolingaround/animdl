import json

import lxml.html as htmlparser

OKRU = "https://ok.ru/"

QUALITY = {
    'mobile': 144,
    'lowest': 240,
    'low': 360,
    'sd': 480,
    'hd': 720
}

SANTIZER = {
    '&quot;': '"',
    "\\\\u0026": "&",
    "\\u0026": "&",
    "\\u003E": ">",
    "\\u003C": "<",
    "\\<": "<",
    "\\>": ">",
    "&amp;": "&",
}

def sanitize(content, *, sanitizer=SANTIZER):
    for k, v in sanitizer.items():
        content = content.replace(k, v)
    return content

def extract(session, url, **opts):
    response = session.get(url)
    
    if response.status_code >= 400:
        return []

    metadata = htmlparser.fromstring(response.text).cssselect('div[data-module="OKVideo"]')

    if not metadata:
        return []

    data_opts = json.loads(json.loads(sanitize(metadata[0].get('data-options'))).get('flashvars', {}).get('metadata'))

    def fast_yield():
        for videos in data_opts.get('videos', []):
            yield {'quality': QUALITY.get(videos.get('name'), 1080), 'stream_url': videos.get('url'), 'headers': {'referer': OKRU}}

    return list(fast_yield()) + [{'stream_url': data_opts.get('hlsManifestUrl'), 'headers': {'referer': OKRU}}]
