import regex
import logging

STREAMTAPE_REGEX = regex.compile(r"'robotlink'\)\.innerHTML = '(.+?)'\+ \('xcd(.+?)'\)")


def extract(session, url, **opts):
    """
    A safe extraction for Streamtape.
    """
    logger = logging.getLogger("streamtape-extractor")
    streamtape_embed_page = session.get(url)
    regex_match = STREAMTAPE_REGEX.search(streamtape_embed_page.text)
    if not regex_match:
        logger.warning(
            "Could not find stream links. {}".format(
                "The file was deleted."
                if streamtape_embed_page.status_code == 404
                else "Failed to extract from: {}".format(url)
            )
        )
        return []

    content_get_uri = "https:{}".format("".join(regex_match.groups()))

    streamtape_redirect = session.get(content_get_uri, follow_redirects=False)
    return [{"stream_url": streamtape_redirect.headers.get("location")}]
