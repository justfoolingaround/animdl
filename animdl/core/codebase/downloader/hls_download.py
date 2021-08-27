import logging
import re
import time

import httpx
import yarl
from Cryptodome.Cipher import AES

from ...config import AUTO_RETRY, QUALITY

ENCRYPTION_DETECTION_REGEX = re.compile(r"#EXT-X-KEY:METHOD=([^,]+),")
ENCRYPTION_URL_IV_REGEX = re.compile(
    r"#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI=\"(?P<key_uri>[^\"]+)\"(?:,IV=(?P<iv>.*))?")

QUALITY_REGEX = re.compile(
    r'#EXT-X-STREAM-INF:.*RESOLUTION=\d+x(?P<quality>\d+).*\n(?P<content_uri>.*)')
TS_EXTENSION_REGEX = re.compile(r"(?P<ts_url>.*\.ts.*)")


def get_extension(url):
    initial, _, extension = yarl.URL(url).name.partition('.')
    return extension


def def_iv(initial=1):
    while True:
        yield initial.to_bytes(16, 'big')
        initial += 1


default_iv_generator = def_iv()


def get_decrypter(key, *, iv=b''):
    if not iv:
        iv = next(default_iv_generator)
    return AES.new(key, AES.MODE_CBC, iv).decrypt


def unencrypted(m3u8_content):
    st = ENCRYPTION_DETECTION_REGEX.search(m3u8_content)
    return (not bool(st)) or st.group(1) == 'NONE'


def extract_encryption(m3u8_content):
    return ENCRYPTION_URL_IV_REGEX.search(m3u8_content).group('key_uri', 'iv')


def m3u8_generation(session_init, m3u8_uri):
    m3u8_uri_parent = yarl.URL(m3u8_uri).parent
    response = session_init(m3u8_uri)
    for quality, content_uri in QUALITY_REGEX.findall(response.text):
        url = yarl.URL(content_uri)
        if get_extension(url) == 'm3u8':
            if not url.is_absolute():
                content_uri = m3u8_uri_parent.join(content_uri)
            yield from m3u8_generation(session_init, content_uri)
        yield {'quality': quality, 'stream_url': content_uri}


def select_best(q_dicts, preferred_quality):
    return (
        sorted(
            [
                q for q in q_dicts if get_extension(
                    q.get('stream_url')) in [
                    'm3u', 'm3u8'] and q.get(
                        'quality', '0').isdigit() and int(
                            q.get(
                                'quality', 0)) <= preferred_quality], key=lambda q: int(
                                    q.get(
                                        'quality', 0)), reverse=True) or q_dicts)[0]


def hls_yield(session, q_dicts, preferred_quality=QUALITY):
    """
    A fast and efficient HLS content yielder.
    """
    logger = logging.getLogger("requests.Session @ 0x%16X".format(id(session)))

    selected = select_best(q_dicts, preferred_quality)

    headers = selected.get('headers', {})
    ssl_verification = headers.get('ssl_verification', True)

    streams = [
        *
        m3u8_generation(
            lambda s: session.get(
                s,
                headers=headers),
            selected.get('stream_url'))]
    second_selection = select_best(streams or [selected], preferred_quality)

    if preferred_quality != int(second_selection.get('quality')):
        logging.warning('Could not find the quality {}, falling back to {}.'.format(
            preferred_quality, second_selection.get('quality') or "an unknown quality."))

    m3u8_response = session.get(second_selection.get('stream_url'), headers=headers)
    m3u8_data = m3u8_response.text

    encryption_uri, encryption_iv, encryption_data = None, None, b''
    encryption_state = not unencrypted(m3u8_data)

    if encryption_state:
        encryption_uri, encryption_iv = extract_encryption(m3u8_data)
        encryption_key_response = session.get(encryption_uri, headers=headers)
        encryption_data = encryption_key_response.content

    all_ts = TS_EXTENSION_REGEX.findall(m3u8_data)
    last_yield = 0

    relative_url = yarl.URL(second_selection.get('stream_url', '')).parent

    for c, ts_uris in enumerate(all_ts, 1):
        url = yarl.URL(ts_uris)
        if not url.is_absolute():
            ts_uris = relative_url.join(ts_uris)
        
        while last_yield != c:
            try:
                ts_response = session.get(ts_uris, headers=headers)
                ts_data = ts_response.content
                if encryption_state:
                    ts_data = get_decrypter(
                        encryption_data, iv=encryption_iv or b'')(ts_data)
                yield {'bytes': ts_data, 'total': len(all_ts), 'current': c}
                last_yield = c
            except httpx.HTTPError as e:
                logger.error(
                    'HLS downloading error due to "{!r}", retrying.'.format(e))
                time.sleep(AUTO_RETRY)
