from .....config import NINEANIME

import regex
import logging

SKEY_RE = regex.compile(r"skey = '(?P<skey>[^']+)';")


def extract(session, vidstream_uri):
    """
    A safe extraction for VidStream.
    """
    info_ajax = "{}/info/{}".format(*regex.search(
        '(.+)/(?:embed|e)/(.+)', vidstream_uri).group(1, 2))
    logger = logging.getLogger('9anime-vidstream-extractor')

    vidstream_content = session.get(
        vidstream_uri, headers={
            'referer': NINEANIME})
    skey_match = SKEY_RE.search(vidstream_content.text)
    if not skey_match:
        if vidstream_content.ok:
            logger.warning(
                'Could not find session key from VidStream; associated url: "%s" (Include this in your GitHub issue!).' %
                vidstream_uri)
        return []

    vidstream_info = session.get(
        info_ajax, params={
            'skey': skey_match.group('skey')}, headers={
            'referer': vidstream_uri})
    return [
        {
            'stream_url': content.get(
                'file', ''), 'headers': {
                'referer': vidstream_uri}} for content in vidstream_info.json().get(
            'media', {}).get(
            'sources', []) if not content.get('file', '').endswith('m3u8')]


extract.site = "vidstream"
