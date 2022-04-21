import base64
import json

import regex
import yarl
from Cryptodome.Cipher import AES


KEYS_REGEX = regex.compile(rb"(?:container|videocontent)-(\d+)")
ENCRYPTED_DATA_REGEX = regex.compile(rb'data-value="(.+?)"')




def get_quality(url_text):
    match = regex.search(r"(\d+) P", url_text)

    if not match:
        return None

    return int(match.group(1))


def pad(data):
    return data + chr(len(data) % 16) * (16 - len(data) % 16)


def aes_encrypt(data: str, *, key, iv):
    return base64.b64encode(
        AES.new(key, AES.MODE_CBC, iv=iv).encrypt(pad(data).encode())
    )


def aes_decrypt(data: str, *, key, iv):
    return (
        AES.new(key, AES.MODE_CBC, iv=iv)
        .decrypt(base64.b64decode(data))
        .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
    )


def extract(session, url, **opts):
    """
    Extract content off of GogoAnime.

    Next time you dare change gogo, I'll add a trace to your
    stupid site's JS and automate the Python code conversion
    from there.

    Now, now, there's no fun in the games where your opponent
    is faster than you by a landslide, is it?

    Resistance is futile.
    """
    parsed_url = yarl.URL(url)
    content_id = parsed_url.query["id"]
    next_host = "https://{}/".format(parsed_url.host)

    streaming_page = session.get(url).content

    encryption_key, iv, decryption_key = (
        _.group(1) for _ in KEYS_REGEX.finditer(streaming_page)
    )

 
    data={
        "id":aes_encrypt(content_id, key=encryption_key, iv=iv).decode(),
        "alias":content_id
    }
    
    token= aes_decrypt(
            ENCRYPTED_DATA_REGEX.search(streaming_page).group(1),
            key=encryption_key,
            iv=iv,
        ).decode()


    ajax_response = session.get(
        yarl.URL(next_host).with_path("encrypt-ajax.php").with_query(data).human_repr()
         +"&{}".format(token),
        headers={"x-requested-with": "XMLHttpRequest"},
    )
    
    content = json.loads(
        aes_decrypt(ajax_response.json().get("data"), key=decryption_key, iv=iv)
    )

    def yielder():
        for origin in content.get("source"):
            yield {
                "stream_url": origin.get("file"),
                "quality": get_quality(origin.get("label", "")),
                "headers": {"referer": next_host},
            }

        for backups in content.get("source_bk"):
            yield {
                "stream_url": backups.get("file"),
                "quality": get_quality(origin.get("label", "")),
                "headers": {"referer": next_host},
            }

    return list(yielder())
