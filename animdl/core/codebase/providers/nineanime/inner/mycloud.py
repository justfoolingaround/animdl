from .....config import NINEANIME

import regex
import logging

SKEY_RE = regex.compile(r"skey = '(?P<skey>[^']+)';")


def uri_correction(mcloud_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    content_id = regex.search(r"embed/(\w+)", mcloud_uri).group(1)
    return "https://mcloud.to/info/%s" % content_id, "https://mcloud.to/embed/%s" % content_id


def extract(session, mcloud_uri):
    """
    A safe extraction for MyCloud.
    """
    info_ajax = "{}/info/{}".format(*regex.search(
        '(.+)/(?:embed|e)/(.+)', mcloud_uri).group(1, 2))
    logger = logging.getLogger('9anime-mycloud-extractor')

    mcloud_content = session.get(mcloud_uri, headers={'referer': NINEANIME})
    skey_match = SKEY_RE.search(mcloud_content.text)
    if not skey_match:
        if mcloud_content.ok:
            logger.warning(
                'Could not find session key from MyCloud; associated url: "%s" (Include this in your GitHub issue!).' %
                mcloud_uri)
        return []

    mcloud_info = session.get(
        info_ajax, params={
            'skey': skey_match.group('skey')}, headers={
            'referer': mcloud_uri})
    return [
        {
            'stream_url': content.get(
                'file', ''), 'headers': {
                'referer': mcloud_uri}} for content in mcloud_info.json().get(
            'media', {}).get(
            'sources', [])]


extract.site = "mycloud"
