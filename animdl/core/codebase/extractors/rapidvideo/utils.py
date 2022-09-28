from base64 import b64decode
from hashlib import md5

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad


def generate_key_from_salt(salt: bytes, secret, *, output=48):

    key = md5(secret + salt).digest()
    current_key = key

    while len(current_key) < output:
        key = md5(key + secret + salt).digest()
        current_key += key

    return current_key[:output]


def decipher_salted_aes(encoded_url: str, secret, *, aes_mode=AES.MODE_CBC):

    raw_value = b64decode(encoded_url.encode("utf-8"))
    assert raw_value.startswith(b"Salted__"), "Not a salt."
    key = generate_key_from_salt(raw_value[8:16], secret)

    return (
        unpad(AES.new(key[:32], aes_mode, key[32:]).decrypt(raw_value[16:]), 16)
        .decode("utf-8", "ignore")
        .lstrip(" ")
    )
