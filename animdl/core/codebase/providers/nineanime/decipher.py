from urllib.parse import unquote
import base64


def decipher(encrypted_url: str):

    s1, s2 = encrypted_url[:16], encrypted_url[16:]

    decrypted = unquote("".join(chr(x) for x in base64.b64decode(s2)))
    mapper = {byte_index: byte_index for byte_index in range(0x100)}
    xcrypto = 0

    for byte_index in range(0x100):
        xcrypto = (
            xcrypto + mapper.get(byte_index) + ord(s1[byte_index % len(s1)])
        ) % 0x100
        mapper[byte_index], mapper[xcrypto] = mapper[xcrypto], mapper[byte_index]

    xcryptoz, xcryptoy = 0, 0

    for character in decrypted:
        xcryptoy = (xcryptoy + 1) % 0x100
        xcryptoz = (xcryptoz + mapper.get(xcryptoy)) % 0x100
        mapper[xcryptoy], mapper[xcryptoz] = mapper[xcryptoz], mapper[xcryptoy]
        yield chr(
            ord(character) ^ mapper[(mapper[xcryptoy] + mapper[xcryptoz]) % 0x100]
        )
