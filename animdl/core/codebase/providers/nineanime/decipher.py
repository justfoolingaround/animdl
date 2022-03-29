from urllib.parse import unquote, quote
from textwrap import wrap
import base64

NORMAL_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BASE64_TABLE = "0wMrYU+ixjJ4QdzgfN2HlyIVAt3sBOZnCT9Lm7uFDovkb/EaKpRWhqXS5168ePcG"


def cipher_keyed(key, plaintext):
    cipher = ""
    xcrypto = 0

    mapping = {_: _ for _ in range(256)}

    for c in range(256):
        xcrypto = (xcrypto + mapping[c] + ord(key[c % len(key)])) % 256
        mapping[c], mapping[xcrypto] = mapping[xcrypto], mapping[c]

    i = j = 0
    for f in range(0, len(plaintext)):
        j = (j + f) % 256
        i = (i + mapping[j]) % 256
        mapping[i], mapping[j] = mapping[j], mapping[i]
        cipher += chr(ord(plaintext[f]) ^ mapping[(mapping[i] + mapping[j]) % 256])

    return cipher


def get_salted_code(plaintext):
    part_1 = encrypt((unquote(plaintext) + "000000")[:6])[0:4][::-1]
    return part_1 + encrypt(cipher_keyed(part_1, unquote(plaintext)))[0:4].replace(
        "=", ""
    )


def encrypt(data):
    return "".join(
        BASE64_TABLE[
            int(segment.ljust(6, "0"), 2) if len(segment) < 6 else int(segment, 2)
        ]
        for segment in wrap(
            "".join(bin(ord(c)).lstrip("0b").rjust(8, "0") for c in data), 6
        )
    )


def decrypt_url(encrypted_url, n=6):
    return unquote(cipher_keyed(encrypted_url[:n], decrypt(encrypted_url[n:])))


def encrypt_url(url):
    return "kr1337" + encrypt(cipher_keyed("kr1337", quote(url)))


def decrypt(data):
    return "".join(
        map(
            chr,
            base64.b64decode(
                (data + "=" * (len(data) % 4))
                .translate(str.maketrans(BASE64_TABLE, NORMAL_TABLE))
                .encode()
            ),
        )
    )
