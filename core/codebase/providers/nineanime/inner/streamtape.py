import re
import logging

STREAMTAPE_REGEX = re.compile(r"innerHTML = \"//([^\"]+)\" \+ '([^']+)'")


def uri_correction(streamtape_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    return "https://streamtape.com/e/%s" % re.search(
        r"e/(\w+)/?", streamtape_uri).group(1)


def extract(session, streamtape_uri):
    """
    A safe extraction for Streamtape.
    """
    logger = logging.getLogger('9anime-streamtape-extractor')
    streamtape_uri = uri_correction(streamtape_uri)
    with session.get(streamtape_uri) as streamtape_embed_page:
        regex_match = STREAMTAPE_REGEX.search(streamtape_embed_page.text)
        if not regex_match:
            logger.warning("Could not find stream links. {}".format(
                "The file was deleted." if streamtape_embed_page.status_code == 404 else 'Failed to extract from: {}'.format(streamtape_uri)))
            return []
        content_get_uri = "https://%s" % ''.join(regex_match.group(1, 2))

    with session.get(content_get_uri, allow_redirects=False, headers={'referer': streamtape_uri}) as streamtape_redirect:
        return [{'quality': 'unknown',
                 'stream_url': streamtape_redirect.headers.get('location')}]


extract.site = "streamtape"
