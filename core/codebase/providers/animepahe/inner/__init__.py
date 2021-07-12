import re
from base64 import b64decode

from .decrypter import decrypt

YTSM = re.compile(r"ysmm = '([^']+)")
KWIK_F_URL = re.compile(r"[&f]/(.+)")
LOCKED_AD = re.compile(r'&url=([^&]+)')

KWIK_PARAMS_RE = re.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
KWIK_D_URL = re.compile(r'action="([^"]+)"')
KWIK_D_TOKEN = re.compile(r'value="([^"]+)"')

def decode_adfly(coded_key):
    r, j = '', ''
    for n, l in enumerate(coded_key):
        if not n % 2: 
            r += l
        else: 
            j = l + j

    encoded_uri = list(r + j)
    numbers = ((i, n) for i, n in enumerate(encoded_uri) if str.isdigit(n))
    for first, second in zip(numbers, numbers):
        xor = int(first[1]) ^ int(second[1])
        if xor < 10:
            encoded_uri[first[0]] = str(xor)

    return b64decode(("".join(encoded_uri)).encode("utf-8"))[16:-16].decode('utf-8', errors='ignore')

def bypass_adfly(session, adfly_url):
    """
    Instant extraction of the adfly url for bots.
    """
    response_code = 302
    while response_code != 200:
        adfly_content = session.get(session.get(adfly_url, allow_redirects=False).headers.get('location'), allow_redirects=False)
        response_code = adfly_content.status_code
    return decode_adfly(YTSM.search(adfly_content.text).group(1))

def get_stream_url_from_kwik(session, adfly_url):
    f_content = session.get(bypass_adfly(session, adfly_url), headers={'referer': 'https://kwik.cx/'})
    decrypted = decrypt(*KWIK_PARAMS_RE.search(f_content.text).group(1,2,3,4))
    return session.post(KWIK_D_URL.search(decrypted).group(1), allow_redirects=False, data={'_token': KWIK_D_TOKEN.search(decrypted).group(1)}, headers={'referer': f_content.url, 'cookie': f_content.headers.get('set-cookie')}).headers.get('location')
