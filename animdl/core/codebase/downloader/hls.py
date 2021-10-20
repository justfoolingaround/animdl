import logging
import regex
import time

import httpx
import yarl
from Cryptodome.Cipher import AES


ENCRYPTION_DETECTION_REGEX = regex.compile(r"#EXT-X-KEY:METHOD=([^,]+),")
ENCRYPTION_URL_IV_REGEX = regex.compile(
    r"#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI=\"(?P<key_uri>[^\"]+)\"(?:,IV=(?P<iv>.*))?")


STREAM_INFO_REGEX = regex.compile(r"#EXT-X-STREAM-INF:(.*)\s+(.+)")
QUALITY_REGEX = regex.compile(
    r'RESOLUTION=\d+x(\d+)')

TS_EXTENSION_REGEX = regex.compile(r"(?P<ts_url>.*\.ts.*)")

HLS_STREAM_EXTENSIONS = ['m3u8', 'm3u']


def get_extension(url):
    initial, _, extension = yarl.URL(url).name.partition('.')
    return extension


def extract_resolution(quality_string):
    resolution = QUALITY_REGEX.search(quality_string)
    if resolution:
        return resolution.group(1)


def def_iv(initial=1):
    while True:
        yield initial.to_bytes(16, 'big')
        initial += 1


def get_decrypter(key, *, iv=b'', default_iv_generator):
    if not iv:
        iv = next(default_iv_generator)
    return AES.new(key, AES.MODE_CBC, iv).decrypt


def unencrypted(m3u8_content):
    st = ENCRYPTION_DETECTION_REGEX.search(m3u8_content)
    return (not bool(st)) or st.group(1) == 'NONE'


def extract_encryption(m3u8_content):
    return ENCRYPTION_URL_IV_REGEX.search(m3u8_content).group('key_uri', 'iv')

def join_url(parent, child):
    return yarl.URL("{}/{}".format(str(parent).rstrip('/'), str(child).lstrip('/')))


def m3u8_generation(session_init, m3u8_uri):
    m3u8_uri_parent = yarl.URL(m3u8_uri).parent
    response = session_init(m3u8_uri)
    for regex_find in STREAM_INFO_REGEX.finditer(
            response.content.decode('utf-8', errors='ignore')):
        stream_info, content_uri = regex_find.groups()
        url = yarl.URL(content_uri)
        if get_extension(url) in HLS_STREAM_EXTENSIONS:
            if not url.is_absolute():
                content_uri = join_url(m3u8_uri_parent, url)
            yield from m3u8_generation(session_init, content_uri)
        yield {'quality': extract_resolution(stream_info), 'stream_url': content_uri}


def sort_by_best(q_dicts, preferred_quality):
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
                                        'quality', 0)), reverse=True) or q_dicts)


def resolve_stream(session, logger, q_dicts, preferred_quality):
    for origin_m3u8 in sort_by_best(q_dicts, preferred_quality):
        headers = origin_m3u8.get('headers', {})
        for m3u8 in sort_by_best(m3u8_generation(lambda s: session.get(
                str(s), headers=headers), origin_m3u8.get('stream_url')), preferred_quality):
            if preferred_quality != int(m3u8.get('quality') or 0):
                logger.warning('Could not find the quality {}, falling back to {}.'.format(
                    preferred_quality, m3u8.get('quality') or "an unknown quality"))
            content_response = session.get(
                str(m3u8.get('stream_url')), headers=headers)
            if content_response.status_code < 400:
                return content_response, origin_m3u8
        content_response = session.get(
            str(origin_m3u8.get('stream_url')), headers=headers)
        if content_response.status_code < 400:
            return content_response, origin_m3u8


def hls_yield(session, q_dicts, preferred_quality,
              auto_retry=2, *, continuation_index=1):
    """
    >>> hls_yield(session, [{'stream_url': 'https://example.com/hls_stream.m3u8'}], 1080) # Generator[dict]

    Returns
    ------
    A dictionary with 3 keys, `bytes`,
    """
    logger = logging.getLogger(
        "{.__class__.__name__} @ 0x{:016X}".format(session, id(session)))
    content_response, origin_m3u8 = resolve_stream(
        session, logger, q_dicts, preferred_quality)
    m3u8_data = content_response.content.decode('utf-8', errors='ignore')
    relative_url = yarl.URL(str(content_response.url).rstrip('/') + "/").parent
    encryption_uri, encryption_iv, encryption_data = None, None, b''
    encryption_state = not unencrypted(m3u8_data)

    if encryption_state:
        encryption_uri, encryption_iv = extract_encryption(m3u8_data)
        parsed_uri = yarl.URL(encryption_uri)
        if not parsed_uri.is_absolute():
            parsed_uri = relative_url.join(parsed_uri)
        encryption_key_response = session.get(
            str(parsed_uri), headers=origin_m3u8.get('headers', {}))
        encryption_data = encryption_key_response.content

    all_ts = TS_EXTENSION_REGEX.findall(m3u8_data)
    default_iv_generator = def_iv(continuation_index)

    for c, ts_uris in enumerate(
            all_ts[(continuation_index - 1):], continuation_index):
        ts_uris = yarl.URL(ts_uris)
        if not ts_uris.is_absolute():
            ts_uris = relative_url.join(ts_uris)
        sucessful_yield = False
        while not sucessful_yield:
            try:
                ts_response = session.get(
                    str(ts_uris), headers=origin_m3u8.get(
                        'headers', {}))
                ts_data = ts_response.content
                if encryption_state:
                    ts_data = get_decrypter(
                        encryption_data, iv=encryption_iv or b'', default_iv_generator=default_iv_generator)(ts_data)
                yield {'bytes': ts_data, 'total': len(all_ts), 'current': c}
                sucessful_yield = True
            except httpx.HTTPError as e:
                logger.error(
                    'HLS downloading error due to "{!r}", retrying.'.format(e))
                time.sleep(auto_retry)
