import base64
import functools

import regex
import requests


def rot47(string):
    for c in string:
        char_code = ord(c)
        yield c if not (33 <= char_code <= 126) else chr(33 + ((char_code + 14) % 94))

YUUMARI = "https://api.yuumari.com/ex-alb/"

headers = { 
    'X-Requested-With': 'XMLHttpRequest',
    'X-Meow': b"\x6d\x65\xba\x6f\x77",
}

@functools.lru_cache()
def access_key():
    api = requests.get(YUUMARI + "_/", headers=headers)
    encoded_key = bytes.fromhex(api.json().get('access_key', ''))
    return ''.join(rot47(base64.b64decode(encoded_key + b"="*(len(encoded_key) % 4)).decode('ascii')))

def bypass(site_url):
    return requests.post(YUUMARI, data={'l': site_url, 'u': access_key()}, headers=headers).json().get('result')

def bypass_ddos_guard(session, base_uri):
    js_bypass_uri = regex.search(
        r"'(.*?)'",
        session.get('https://check.ddos-guard.net/check.js').text).group(1)
    
    session.get(base_uri + js_bypass_uri)
