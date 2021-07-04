import re
import time

import requests
from Cryptodome.Cipher import AES

from ...config import QUALITY, AUTO_RETRY

ENCRYPTION_DETECTION_REGEX = re.compile(r"#EXT-X-KEY:METHOD=([^,]+),")
ENCRYPTION_URL_IV_REGEX = re.compile(r"#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI=\"(?P<key_uri>[^\"]+)\"(?:,IV=(?P<iv>.*))?")

QUALITY_REGEX = re.compile(r'#EXT-X-STREAM-INF:.*RESOLUTION=.*x(?P<quality>.*)\n(?P<content_uri>.*)')
M3U8_EXTENSION_REGEX = re.compile(r"(?P<m3u8_url>.*\.m3u8.*)")
TS_EXTENSION_REGEX = re.compile(r"(?P<ts_url>.*\.ts.*)")

REL_URL_REGEX = re.compile(r"(?P<url_base>(?:https?://)?.*)/")

URL_REGEX = re.compile(r"(?:https?://)?(?:\S+\.)+(?:[^/]+/)+(?P<url_end>[^?/]+)")

def absolute_extension_determination(url):
    """
    Making use of the best regular expression I've ever seen.
    """
    match = URL_REGEX.search(url)
    if match:
        url_end = match.group('url_end')
        return '' if url_end.rfind('.') == -1 else url_end[url_end.rfind('.') + 1:]
    return ''

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

def m3u8_generation(session_init, m3u8_uri, *, is_origin=True):
    with session_init(m3u8_uri) as response:
        for quality, content_uri in QUALITY_REGEX.findall(response.text):
            if M3U8_EXTENSION_REGEX.search(content_uri):
                if not re.search(r'\S+://', content_uri):
                    content_uri = "%s/%s" % (REL_URL_REGEX.search(m3u8_uri).group('url_base'), content_uri)
                yield from m3u8_generation(session_init, content_uri, is_origin=False)
            yield {'quality': quality, 'stream_url': content_uri}

def select_best(q_dicts, preferred_quality):
    return (sorted([q for q in q_dicts if absolute_extension_determination(q.get('stream_url')) in ['m3u', 'm3u8'] and q.get('quality').isdigit() and int(q.get('quality')) <= preferred_quality], key=lambda q: int(q.get('quality')), reverse=True) or q_dicts)[0]


def hls_yield(session, q_dicts, preferred_quality=QUALITY):
    """
    A fast and efficient HLS content yielder.
    """
    selected = select_best(q_dicts, preferred_quality)
    
    headers = selected.get('headers')
    ssl_verification = headers.get('ssl_verification', True)
    
    second_selection = select_best([*m3u8_generation(lambda s: session.get(s, headers=headers), selected.get('stream_url'))] or [selected], preferred_quality)

    with session.get(second_selection.get('stream_url'), headers=headers, verify=ssl_verification) as m3u8_response:
        m3u8_data = m3u8_response.text

    encryption_uri, encryption_iv, encryption_data = None, None, b''
    encryption_state = not unencrypted(m3u8_data)

    if encryption_state:
        encryption_uri, encryption_iv = extract_encryption(m3u8_data)
        with session.get(encryption_uri, headers=headers, verify=ssl_verification) as encryption_key_response:
            encryption_data = encryption_key_response.content

    all_ts = TS_EXTENSION_REGEX.findall(m3u8_data)
    last_yield = 0

    for c, ts_uris in enumerate(all_ts, 1):
        if not re.search(r'\S+://', ts_uris):
            ts_uris = "%s/%s" % (REL_URL_REGEX.search(second_selection.get('stream_url')).group('url_base'), ts_uris)

        while last_yield != c:
            try:
                with session.get(ts_uris, headers=headers, verify=ssl_verification) as ts_response:
                    ts_data = ts_response.content
                    if encryption_state:
                        ts_data = get_decrypter(encryption_data, iv=encryption_iv or b'')(ts_data)
                    yield {'bytes': ts_data, 'total': len(all_ts), 'current': c}
                last_yield = c
            except requests.RequestException as e:
                print("[\x1b[31manimdl-hls-exception\x1b[39m] {}".format('Downloading error due to "{!r}", retrying.'.format(e)))
                time.sleep(AUTO_RETRY)