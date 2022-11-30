from base64 import b64decode

import regex

YTSM = regex.compile(r"ysmm = '([^']+)")


def decode_adfly(coded_key):
    r, j = "", ""
    for n, l in enumerate(coded_key):
        if n & 1:
            r += l
        else:
            j = l + j

    encoded_uri = list(r + j)
    numbers = ((i, n) for i, n in enumerate(encoded_uri) if str.isdigit(n))
    for first, second in zip(numbers, numbers):
        xor = int(first[1]) ^ int(second[1])
        if xor < 10:
            encoded_uri[first[0]] = str(xor)

    return b64decode(("".join(encoded_uri)).encode("utf-8"))[16:-16].decode(
        "utf-8", errors="ignore"
    )


def bypass_adfly(session, adfly_url):

    response_code = 302

    while response_code != 200:
        adfly_content = session.get(
            session.get(adfly_url, follow_redirects=False).headers.get("location"),
            follow_redirects=False,
        )
        response_code = adfly_content.status_code
    return decode_adfly(YTSM.search(adfly_content.text).group(1))
