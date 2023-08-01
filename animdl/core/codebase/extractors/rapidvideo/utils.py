from base64 import b64decode
from hashlib import md5

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad


def pkcs5_bytes_to_key(salt: bytes, secret, *, output=48, hash_module=md5):
    key = hash_module(secret + salt).digest()
    current_key = key

    while len(current_key) < output:
        key = hash_module(key + secret + salt).digest()
        current_key += key

    return current_key[:output]


def decipher_salted_aes(encoded_url: str, key_finders, *, aes_mode=AES.MODE_CBC):
    pwd_from_url = ""
    untouched_url = encoded_url

    for start, end in key_finders:
        pwd_from_url += untouched_url[start:end]
        encoded_url = encoded_url.replace(untouched_url[start:end], "")

    raw_value = b64decode(encoded_url.encode("utf-8"))

    assert raw_value.startswith(b"Salted__"), "Not a salt."

    key = pkcs5_bytes_to_key(raw_value[8:16], pwd_from_url.encode("utf-8"))
    return (
        unpad(AES.new(key[:32], aes_mode, key[32:]).decrypt(raw_value[16:]), 16)
        .decode("utf-8", "ignore")
        .lstrip(" ")
    )
