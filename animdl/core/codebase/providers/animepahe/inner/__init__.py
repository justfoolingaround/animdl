import regex

KWIK_PARAMS_RE = regex.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
KWIK_D_URL = regex.compile(r'action="(.+?)"')
KWIK_D_TOKEN = regex.compile(r'value="(.+?)"')

KWIK_REDIRECTION_RE = regex.compile(r'<a href="(.+?)" .+?>Redirect me</a>')

CHARACTER_MAP = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"


def get_string(content, s1, s2):

    slice_2 = CHARACTER_MAP[0:s2]

    acc = 0
    for n, i in enumerate(content[::-1]):
        acc += int(i if i.isdigit() else 0) * s1**n

    k = ""
    while acc > 0:
        k = slice_2[int(acc % s2)] + k
        acc = (acc - (acc % s2)) / s2

    return k or "0"


def decrypt(full_string, key, v1, v2):
    v1, v2 = int(v1), int(v2)
    r = ""
    i = 0
    while i < len(full_string):
        s = ""
        while full_string[i] != key[v2]:
            s += full_string[i]
            i += 1
        j = 0
        while j < len(key):
            s = s.replace(key[j], str(j))
            j += 1
        r += chr(int(get_string(s, v2, 10)) - v1)
        i += 1
    return r


def get_animepahe_url(session, pahe_win_url):

    response = session.get(pahe_win_url)
    response.raise_for_status()

    url = KWIK_REDIRECTION_RE.search(response.text).group(1)

    download_page = session.get(url)

    full_key, key, v1, v2 = KWIK_PARAMS_RE.search(download_page.text).group(1, 2, 3, 4)

    decrypted = decrypt(
        full_key,
        key,
        v1,
        v2,
    )

    content = session.post(
        KWIK_D_URL.search(decrypted).group(1),
        follow_redirects=False,
        data={"_token": KWIK_D_TOKEN.search(decrypted).group(1)},
        headers={
            "Referer": "https://kwik.cx/",
        },
    )

    return content.headers["Location"]
