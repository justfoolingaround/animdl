import functools

import httpx

BYPASS_SERVER = "https://cr-unblocker.us.to/start_session"

headers = httpx.Headers(
    {
        b"Accept": b"*/*",
        b"Accept-Encoding": b"gzip, deflate",
        b"Connection": b"keep-alive",
        b"Referer": b"https://google.com/",
        b"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36".encode('ascii')
    }
)


@functools.lru_cache()
def get_session_id():
    return httpx.get(BYPASS_SERVER, params={'version': '1.1'}).json().get(
        'data', {}).get('session_id')


def geobypass_response(url):
    return httpx.get(url, headers=headers, cookies={
                     'session_id': get_session_id()})
