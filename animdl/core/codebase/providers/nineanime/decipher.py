import base64
from urllib.parse import quote, unquote
from Cryptodome.Cipher import ARC4

VRF_KEY = b"iECwVsmW38Qe94KN"
URL_KEY = b"hlPeNwkncH0fq9so"
CHAR_SUBST_OFFSETS = [-4, -4, 3, 3, 6, -4, 3, -6, -2, -4]

def vrf_gen(vid_id):
    vrf = quote(vid_id)
    vrf = ARC4.new(VRF_KEY).encrypt(vid_id.encode())
    vrf = base64.b64encode(vrf).decode()
    vrf = char_subst(vrf, CHAR_SUBST_OFFSETS)
    vrf = vrf[::-1]
    vrf = base64.b64encode(vrf.encode()).decode()
    return vrf

def char_subst(string, offsets):
    result = ""
    for i in range(len(string)):
        result += chr(ord(string[i]) + offsets[i % len(offsets)])
    return result

def decrypt_url(encrypted_url):
    url = base64.b64decode(encrypted_url)
    url = ARC4.new(URL_KEY).decrypt(url)
    url = unquote(url.decode())
    return url