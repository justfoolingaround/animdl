import json
import re
from base64 import b64decode, b64encode
from functools import partial

import lxml.html as htmlparser

ID_MATCHER = re.compile(r"(?<=\?id=)[^&]+")

EMBED_URL_BASE = "https://animixplay.to/api/live{}"
EMBED_M3U8_MATCHER = re.compile(r'(?<=player\.html#)[^#]+')
EMBED_VIDEO_MATCHER = re.compile(r'(?<=video=")[^"]+')

def fetching_chain(f1, f2, session, url, check=lambda *args: True):
    return f2(session, f1(session, url), check=check)

def from_site_url(session, url) -> dict:
    """
    Keep in mind that the return of this function will vary from stream to stream. (Gogo Anime streams and 4Anime streams will vary.)
    """
    return json.loads(htmlparser.fromstring(session.get(url).content).xpath('//div[@id="epslistplace"]')[0].text)

def get_stream_url(session, data_url):
    content_id = ID_MATCHER.search(data_url).group(0).encode(errors='ignore')
    while 1:
        embed_page = session.get(EMBED_URL_BASE.format(b64encode(b"%sLTXs3GrU8we9O%s" % (content_id, b64encode(content_id))).decode(errors='ignore')), allow_redirects=True)
        video_on_site = EMBED_VIDEO_MATCHER.search(embed_page.text)
        if video_on_site:
            return [{'stream_url': video_on_site.group(0)}]
        embed_m3u8 = EMBED_M3U8_MATCHER.search(embed_page.url)
        if not embed_m3u8:
            continue
        return [{'stream_url': b64decode(EMBED_M3U8_MATCHER.search(embed_page.url).group(0).encode(errors='ignore')).decode(errors='ignore'), 'quality': 'multi'}]

def gogoanime_parser(session, data: dict, *, check=lambda *args: True):
    for value in range(data.get('eptotal')):
        if check(value + 1):
            yield partial(lambda s, data_url: get_stream_url(s, data_url), session, data[str(value)]), value + 1