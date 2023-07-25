import base64
from urllib.parse import quote, unquote

from Cryptodome.Cipher import ARC4

VRF_KEY = b"iECwVsmW38Qe94KN"
URL_KEY = b"hlPeNwkncH0fq9so"
CHAR_SUBST_OFFSETS = (-4, -4, 3, 3, 6, -4, 3, -6, -2, -4)


def char_subst(content: bytes, *, offsets=CHAR_SUBST_OFFSETS):
    for n, value in enumerate(content):
        yield (value + offsets[n % len(offsets)])


def generate_vrf_from_content_id(
    content_id: str,
    key=VRF_KEY,
    *,
    offsets=CHAR_SUBST_OFFSETS,
    encoding="utf-8",
    reverse_later=True
):
    encoded_id = base64.b64encode(
        ARC4.new(key).encrypt(quote(content_id).encode(encoding))
    )

    if reverse_later:
        encoded_id = bytes(char_subst(encoded_id, offsets=offsets))[::-1]
    else:
        encoded_id = bytes(char_subst(encoded_id[::-1], offsets=offsets))

    return base64.b64encode(encoded_id).decode(encoding)


def decrypt_url(encrypted_url: str, key=URL_KEY, *, encoding="utf-8"):
    return unquote(
        ARC4.new(key).decrypt(base64.b64decode(encrypted_url)).decode(encoding)
    )
