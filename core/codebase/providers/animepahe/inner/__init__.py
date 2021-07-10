import re
from base64 import b64decode

from .decrypter import decrypt

YTSM = re.compile(r"(?<=ysmm = ')[^']+")
KWIK_F_URL = re.compile(r"[&f]/(.+)")
KWIK_PARAMS_RE = re.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
KWIK_D_URL = re.compile(r'action="([^"]+)"')
KWIK_D_TOKEN = re.compile(r'value="([^"]+)"')

def decode_adfly(coded_key):
    
    r, j = '', ''

    for n, l in enumerate(coded_key):
        if n % 2 == 0: 
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

def get_stream_url_from_kwik(session, adfly_url):

    while 1:
        regex_search = YTSM.search(session.get(adfly_url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}).text)
        if not regex_search:
            continue
        kwik = KWIK_F_URL.search(decode_adfly(regex_search.group(0)))
        if not kwik:
            continue
        f_content = session.get("https://kwik.cx/f/%s" % kwik.group(1), headers={'referer': 'https://kwik.cx/'})
        if not f_content.ok:
            continue
        break

    code, key, v1, v2 = KWIK_PARAMS_RE.search(f_content.text).group(1,2,3,4)
    decrypted = decrypt(code, key, int(v1), int(v2))
    d_url = KWIK_D_URL.search(decrypted).group(1)
    token = KWIK_D_TOKEN.search(decrypted).group(1)

    return session.post(d_url, allow_redirects=False, data={'_token': token}, headers={'referer': f_content.url, 'cookie': f_content.headers.get('set-cookie')}).headers.get('location')