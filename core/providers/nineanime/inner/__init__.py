"""
9Anime has 4 sources; and here are 4 custom extractors in an order.

This order is made to ensure perfect yield of content.

- Mp4Upload
- Streamtape
- VidStream
- MyCloud

(each one fall backs in the order when required)
"""

from ....config import NINEANIME

from ..decipher import decipher as decode

from .mp4upload  import extract as extract_1
from .streamtape import extract as extract_2
from .vidstream  import extract as extract_3
from .mycloud    import extract as extract_4

def get_url_by_hash(session, _hash, access_headers):
    with session.get(NINEANIME + "ajax/anime/episode", params={'id': _hash}, headers=access_headers) as ajax_server_response:
        return decode(ajax_server_response.json().get('url', ''))

def fallback_extraction(session, content_json, access_headers):
    
    return extract_1(session, get_url_by_hash(session, content_json.get('35'), access_headers)) or \
        extract_2(session, get_url_by_hash(session, content_json.get('40'), access_headers)) or \
        extract_3(session, get_url_by_hash(session, content_json.get('41'), access_headers)) or \
        extract_4(session, get_url_by_hash(session, content_json.get('28'), access_headers))