"""
Animix raises `503 (Service Temporarily Unavailable)` in these user-agents:

- animdl/1.3

I know what you're doing and you can't stop me, Animix. I'm watching you.
"""

import httpx
import logging

headers = httpx.Headers(
    {
        b"Accept": b"*/*",
        b"Accept-Encoding": b"gzip, deflate",
        b"Connection": b"keep-alive",
        b"Referer": "https://google.com/",
        b"User-Agent": b"animdl/1.3.76"
    }
)

def get_safeoverride(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return None
    return inner

class AnimeHttpClient(httpx.Client):

    http_logger = logging.getLogger("animdl-http")

    def request(self, *args, **kwargs):

        response = super().request(*args, **kwargs)
        
        if response.status_code == 403:
            if b'window._cf_chl_opt' in response.content:
                if logging.root.level > 20:
                    self.http_logger.warning("The response is cloudflare protected and animdl cannot prompt for Cloudflare bypass cookie at this log level.")
                    return response

                self.http_logger.info("Cloudflare was detected in the response for: {.url}.".format(response))

                self.http_logger.info("This issue can be easily be bypassed by following the instructions here: .")

                self.cookies.update({'cf_clearance': input("[*] cf_clearance: ")})
                self.headers.update({'user-agent': input("[*] user-agent: ")})

                response = self.request(*args, **kwargs)


        return response


client = AnimeHttpClient(headers=headers, timeout=30.0)

client.__del__ = get_safeoverride(client.__del__)
