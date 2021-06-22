from Cryptodome.Cipher import AES
from hashlib import md5

from base64 import b64decode
import requests

TWISTMOE_SECRET = b'267041df55ca2b36f2e322d05ee2c9cf'

def unpad_content(content):
    return content[:-(content[-1] if isinstance(content[-1], int) else ord(content[-1]))]

def generate_key(salt: bytes, *, output=48):
    
    key = md5(TWISTMOE_SECRET + salt).digest()
    current_key = key
    
    while len(current_key) < output:
        key = md5(key + TWISTMOE_SECRET + salt).digest()
        current_key += key
        
    return current_key[:output]

def decipher(encoded_url: str):
    
    s1 = b64decode(encoded_url.encode('utf-8'))
    assert s1.startswith(b'Salted__'), "Not a salt."
    key = generate_key(s1[8:16])
    return unpad_content(AES.new(key[:32], AES.MODE_CBC, key[32:]).decrypt(s1[16:])).decode('utf-8', 'ignore').lstrip(' ')

def __internal_get_uri(stream_url):
    """
    Sadly this has no need but since it references previous algorithm, this shall remain unremoved from the code itself.
    """
    return requests.get(stream_url, headers={'referer': 'https://twist.moe'}, allow_redirects=False).headers.get('location', 'https://twist.moe/404')
    
def get_twistmoe_anime_uri(session, anime_name, *, api_url='https://twist.moe/api/anime/{anime_name}'):
    
    base_url = 'https://air-cdn.twist.moe%s' if session.get(api_url.format(anime_name=anime_name), headers={'x-access-token': '0df14814b9e590a1f26d3071a4ed7974'}).json().get('ongoing', 0) else "https://cdn.twist.moe%s"
     
    r = session.get("%s/sources" % api_url.format(anime_name=anime_name), headers={'x-access-token': '0df14814b9e590a1f26d3071a4ed7974'})
    
    if r.status_code != 200:
        return []
    
    return [{'episode_number': anime_episode_info.get('number', 0), 'stream_url': (base_url % decipher(anime_episode_info.get('source', '')))} for anime_episode_info in r.json()]