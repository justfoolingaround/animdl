from base64 import b64decode
from functools import reduce

import lxml.html as htmlparser
import regex
import yarl

DOWNLOAD_URL_RE = regex.compile(r"download\.php\?url=([^?&/]+)")

GARBAGES = [
    'URASDGHUSRFSJGYfdsffsderFStewthsfSFtrfte',
    'AdeqwrwedffryretgsdFrsftrsvfsfsr',
    'werFrefdsfrersfdsrfer36343534',
    'AawehyfcghysfdsDGDYdgdsf',
    'wstdgdsgtert',
    'Adrefsd',
    'sdf',
]

def decrypt_redirect(url):
    is_gogocdn = DOWNLOAD_URL_RE.search(url)
    
    if not is_gogocdn:
        return url

    encrypted_url = reduce(lambda x, y: x.replace(y, ''), GARBAGES, is_gogocdn.group(1))
    
    return b64decode(encrypted_url + "="*(len(encrypted_url) % 4)).decode()


def get_quality(url_text):
    match = regex.search(r'(\d+)P', url_text)
    if not match:
        return None
    return int(match.group(1))


def extract(session, url, **opts):
    parsed_url = yarl.URL(url)

    if not parsed_url.scheme:
        parsed_url = parsed_url.with_scheme('https')

    content_url = parsed_url.with_name('download').with_query(parsed_url.query).human_repr()

    response = session.get(
        content_url,
        headers={
            'referer': url})
    content = htmlparser.fromstring(response.text)

    return [{'quality': get_quality(url.text_content()), 'stream_url': decrypt_redirect(url.get('href')), 'headers': {'referer': url.get('href')}} for url in content.cssselect('.dowload > a[download]')]
