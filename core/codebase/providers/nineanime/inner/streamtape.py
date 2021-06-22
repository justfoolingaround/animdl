import re

STREAMTAPE_REGEX = re.compile(r"innerHTML = \"//([^\"]+)\" \+ '([^']+)'")

def uri_correction(streamtape_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    return "https://streamtape.com/e/%s" % re.search(r"e/(\w+)/?", streamtape_uri).group(1)

def extract(session, streamtape_uri):
    """
    A safe extraction for Streamtape.
    """
    streamtape_uri = uri_correction(streamtape_uri)
    with session.get(streamtape_uri) as streamtape_embed_page:
        content_get_uri = "https://%s" % ''.join(STREAMTAPE_REGEX.search(streamtape_embed_page.text).group(1, 2))
        
    with session.get(content_get_uri, allow_redirects=False, headers={'referer': streamtape_uri}) as streamtape_redirect:
        return [{'quality': 'unknown', 'stream_url': streamtape_redirect.headers.get('location')}]