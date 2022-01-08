"""
Hello, stranger, if you're here to copy the code
yes, you've reached the best and top of the efficiency
chart gogoanime-scraper now. Feel free.

A lot of braincells were used and lost throughout the 
process and for this, if you're going to copy the code, 
have some respect and credit the following developers below:

Without these people, you would have to resort to poo-poo,
inefficient, weird and unreliable alternatives.

(I'm looking at you pystardust/ani-cli, love you guys though)

- brahmkshatriya (https://github.com/brahmkshatriya)

    Associated project: https://github.com/saikou-app/saikou

- KR (https://github.com/justfoolingaround)

    Associated project: https://github.com/justfoolingaround/animdl

I recommend you to not mention anything of "decrypted" or 
"fixed" in your code commits to avoid the site devs to change
algorithms or even reCaptcha gate the encrypted endpoint.

This is encryption, uncharted seas for most of the developer
community and things are hard.

Need some help or just want to talk: 
    https://discord.gg/gaX2Snst2j

"""

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

    site_iv = streaming_page.cssselect('script[data-name="ts"]')[0].get('data-value').encode()
    encrypted_ajax = base64.b64encode(AES.new(GOGOANIME_SECRET, AES.MODE_CBC, iv=site_iv).encrypt(pad(parsed_url.query.get('id').replace('%3D', '=')).encode()))

    content = (session.get(
        "{}encrypt-ajax.php?id={}&time=00{}00".format(next_host, encrypted_ajax.decode(), site_iv.decode()),
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
