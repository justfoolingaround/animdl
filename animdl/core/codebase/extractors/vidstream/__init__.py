import regex
import logging

SKEY_RE = regex.compile(r"skey = '(?P<skey>[^']+)';")

def extract(session, url, **opts):
    headers = opts.pop('headers', {})

    info_ajax = "{}/info/{}".format(*regex.search(
        '(.+)/(?:embed|e)/(.+)', url).group(1, 2))
    logger = logging.getLogger('vidstream-extractor')

    vidstream_content = session.get(
        url, headers=headers)
    skey_match = SKEY_RE.search(vidstream_content.text)
    if not skey_match:
        if vidstream_content.ok:
            logger.warning(
                'Could not find session key from VidStream; associated url: "%s" (Include this in your GitHub issue!).' %
                url)
        return []

    vidstream_info = session.get(
        info_ajax, params={
            'skey': skey_match.group('skey')}, headers={
            'referer': url})
    return [
        {
            'stream_url': content.get(
                'file', ''), 'headers': {
                'referer': url}} for content in vidstream_info.json().get(
            'media', {}).get(
            'sources', []) if not content.get('file', '').endswith('m3u8')]
