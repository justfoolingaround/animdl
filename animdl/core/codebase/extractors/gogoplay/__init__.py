import base64

import lxml.html as htmlparser
import regex
import yarl
from Cryptodome.Cipher import AES

GOGOANIME_SECRET = b"257465385929383"b"96764662879833288"

def get_quality(url_text):
    match = regex.search(r'(\d+) P', url_text)
    if not match:
        return None

    return int(match.group(1))


def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length)*length

def extract(session, url, **opts):
    """
    Extract content off of GogoAnime.
    """
    parsed_url = yarl.URL(url)

    if not parsed_url.scheme:
        parsed_url = parsed_url.with_scheme('https')

    next_host = "https://{}/".format(parsed_url.host)

    streaming_page = htmlparser.fromstring(session.get(parsed_url.human_repr(), headers={'referer': next_host}).text)

    crypto_code = streaming_page.cssselect('meta[name="crypto"]')[0].get('content')
    site_iv = streaming_page.cssselect('script[data-name="ts"]')[0].get('data-value').encode()

    content_id, _, next_args = AES.new(GOGOANIME_SECRET, AES.MODE_CBC, iv=site_iv).decrypt(
        base64.b64decode(crypto_code)
    ).decode('utf-8').rstrip('\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f').partition('&')

    encrypted_ajax = base64.b64encode(AES.new(GOGOANIME_SECRET, AES.MODE_CBC, iv=site_iv).encrypt(pad(content_id.replace('%3D', '=')).encode()))

    content = (session.get(
        "{}encrypt-ajax.php?id={}&{}&time=00{}00".format(next_host, encrypted_ajax.decode(), next_args, site_iv.decode()),
        headers={'x-requested-with': 'XMLHttpRequest'}
    ).json())

    def yielder():
        for origin in content.get('source'):
            yield {
                'stream_url': origin.get('file'), 'quality': get_quality(origin.get('label', '')), 'headers': {'referer': next_host}
            }

        for backups in content.get('source_bk'):
            yield {
                'stream_url': backups.get('file'), 'quality': get_quality(origin.get('label', '')), 'headers': {'referer': next_host}
            }

    return list(yielder())
