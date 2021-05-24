import re

VIDSTREAM_INFO_AJAX = 'https://vidstream.pro/info/%s'
VIDSTREAM_EMBED = "https://vidstream.pro/e/%s"

VIDSTREAM_SLUG_MATCHER = re.compile(r"(?:https?://)?(?:\S+\.)+.\S+/(?:embed|e)/(?P<slug>[A-Z0-9]+)")
VIDSTREAM_SITEKEY_MATCHER = re.compile(r"skey = '(?P<skey>[^']+)';")

def extract(session, content_uri, headers):
    """
    This method uses safe extraction.
    """
    slug_match = VIDSTREAM_SLUG_MATCHER.search(content_uri)
    if not slug_match:
        raise Exception("Could not find slug for VidStream extraction; associated url: %s" % content_uri)
    
    slug = slug_match.group(1)
    
    with session.get(VIDSTREAM_EMBED % slug, headers=headers) as embed_page:
        skey_match = VIDSTREAM_SITEKEY_MATCHER.search(embed_page.text)
        if not skey_match:
            if embed_page.ok:
                raise Exception("Could not find site key from VidStream; possibly due to insufficient headers; associated url: %s" % embed_page.url)
            return []
    skey = skey_match.group(1)
    
    with session.get(VIDSTREAM_INFO_AJAX % slug, params={'skey': skey}, headers={'referer': embed_page.url}) as vidstream_info:
        return [{'quality': content.get('label', 'unknown'), 'stream_url': content.get('file', ''), 'headers': {'referer': embed_page.url}} for content in vidstream_info.json().get('media', {}).get('sources', [])] 