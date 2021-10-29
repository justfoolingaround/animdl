import regex
import time

DOODSTREAM = "https://dood.la/"

PASS_MD5_RE = regex.compile(r"/(pass_md5/.+?)'")
TOKEN_RE = regex.compile(r'\?token=([^&]+)')

def extract(session, url):
    embed_page = session.get(url).text
    return [{"stream_url": "{}doodstream?token={}&expiry={}".format(
        session.get(DOODSTREAM + PASS_MD5_RE.search(embed_page).group(1), headers={'referer': DOODSTREAM}).text,
         TOKEN_RE.search(embed_page).group(1), int(time.time() * 1000)), 'headers': {'referer': DOODSTREAM}}]