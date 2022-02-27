from urllib.parse import unquote, quote
from textwrap import wrap
import base64

NORMAL_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BASE64_TABLE = "0wMrYU+ixjJ4QdzgfN2HlyIVAt3sBOZnCT9Lm7uFDovkb/EaKpRWhqXS5168ePcG"


def encrypt_to_four(plaintext):

    cipher = ""

    for c in range(0, len(plaintext), 3):
        mapping = [ord(plaintext[c]) >> 2, 3 & ord(plaintext[c]) << 4, None, None]

        if len(plaintext) > (c + 1):
            mapping[1] |= ord(plaintext[c + 1]) >> 4
            mapping[2] = (15 & ord(plaintext[c + 1])) << 2

        if len(plaintext) > (c + 2):
            mapping[2] = (mapping[2] or 0) | ord(plaintext[c + 2]) >> 6
            mapping[3] = 63 & ord(plaintext[c + 2])

        for data in mapping:
            if data is None:
                cipher += "="
            else:
                if 0 <= data and data < 64:
                    cipher += BASE64_TABLE[data]

        return cipher


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
    part_1 = encrypt_to_four((unquote(plaintext) + "000000")[:6])[::-1]
    return part_1 + encrypt_to_four(cipher_keyed(part_1, unquote(plaintext))).replace(
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
        chr(_)
        for _ in base64.b64decode(
            data.translate(str.maketrans(BASE64_TABLE, NORMAL_TABLE)).encode()
        )
    )
