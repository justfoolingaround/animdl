import regex
import logging

SKEY_RE = regex.compile(r"skey = '(?P<skey>[^']+)';")


def extract(session, url, **opts):
    headers = opts.pop('headers', {})

    info_ajax = "{}/info/{}".format(*regex.search(
        '(.+)/(?:embed|e)/(.+)', url).group(1, 2))
    logger = logging.getLogger('mycloud-extractor')

    mcloud_content = session.get(url, headers={'referer': headers})
    skey_match = SKEY_RE.search(mcloud_content.text)
    if not skey_match:
        if mcloud_content.ok:
            logger.warning(
                'Could not find session key from MyCloud; associated url: "%s" (Include this in your GitHub issue!).' %
                url)
        return []

    mcloud_info = session.get(
        info_ajax, params={
            'skey': skey_match.group('skey')}, headers={
            'referer': url})
    return [
        {
            'stream_url': content.get(
                'file', ''), 'headers': {
                'referer': url}} for content in mcloud_info.json().get(
            'media', {}).get(
            'sources', [])]
