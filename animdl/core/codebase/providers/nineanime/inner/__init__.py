"""
9Anime has 4 sources; and here are 4 custom extractors in an order.

This order is made to ensure perfect yield of content.

- Mp4Upload
- Streamtape
- VidStream
- MyCloud

(each one fall backs in the order when required)
"""

import json
import logging
import time

from .....config import NINEANIME
from ..decipher import decipher as decode

from .mp4upload import extract as extract_2
from .mycloud import extract as extract_4
from .streamtape import extract as extract_3
from .vidstream import extract as extract_1


def validate_json_content_yield(
        session,
        url,
        ensurer=lambda *args,
        **kwargs: True,
        max_tries=5,
        **session_kwargs):
    """
    9Anime throws 500s if fast paced traffic is seen; this function combats that.
    """
    c = False
    while not c:
        time.sleep(.3)
        response = session.get(url, **session_kwargs)
        c = response.ok and ensurer(response)
        max_tries -= 1
        if not max_tries:
            raise Exception(
                'Max tries exceeded with the given provider mirror.')
    return json.loads(response.text)


def fallback_handler(f, session, _hash_cb):
    logger = logging.getLogger('9anime-fallback-handler')
    try:
        return f(session, _hash_cb())
    except Exception as e:
        logger.warning(
            'Falling back to mirrors due to an unexpected error: {} with the provider {}. If the problem persists, make sure to raise an issue!'.format(
                e,
                f.site))
    return []


def get_url_by_hash(session, _hash, access_headers):
    return ''.join(
        decode(
            validate_json_content_yield(
                session,
                NINEANIME +
                "ajax/anime/episode",
                ensurer=lambda r: json.loads(
                    r.text).get('url'),
                params={
                    'id': _hash},
                headers=access_headers).get(
                'url',
                '')))


def fallback_extraction(session, content_json, access_headers):

    return fallback_handler(
        extract_1,
        session,
        lambda: get_url_by_hash(
            session,
            content_json.get('41'),
            access_headers)) or fallback_handler(
        extract_2,
        session,
        lambda: get_url_by_hash(
            session,
            content_json.get('35'),
            access_headers)) or fallback_handler(
        extract_3,
        session,
        lambda: get_url_by_hash(
            session,
            content_json.get('40'),
            access_headers)) or fallback_handler(
        extract_4,
        session,
        lambda: get_url_by_hash(
            session,
            content_json.get('28'),
            access_headers))
