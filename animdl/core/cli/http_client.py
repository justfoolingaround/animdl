import httpx

headers = httpx.Headers(
    {
        b"Accept": b"*/*",
        b"Accept-Encoding": b"gzip, deflate",
        b"Connection": b"keep-alive",
        b"Referer": "https://google.com/",
        b"User-Agent": b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.99 Safari/537.36"
    }
)

def get_safeoverride(f):
    def inner(*args, **kwargs):
        try:
            retval = f(*args, **kwargs)
        except:
            return None
        return retval
    return inner

client = httpx.Client(headers=headers, timeout=30.0)

client.__del__ = get_safeoverride(client.__del__)
