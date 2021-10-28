"""
Animix raises `503 (Service Temporarily Unavailable)` in these user-agents:

- animdl/1.3

I know what you're doing and you can't stop me, Animix. I'm watching you.
"""

import httpx

headers = httpx.Headers(
    {
        b"Accept": b"*/*",
        b"Accept-Encoding": b"gzip, deflate",
        b"Connection": b"keep-alive",
        b"Referer": "https://google.com/",
        b"User-Agent": b"animdl/1.3.73"
    }
)

def get_safeoverride(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return None
    return inner

client = httpx.Client(headers=headers, timeout=30.0)

client.__del__ = get_safeoverride(client.__del__)
