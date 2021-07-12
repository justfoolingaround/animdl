import re
import time

import requests
from tqdm import tqdm

from ...config import AUTO_RETRY, QUALITY
from .hls_download import hls_yield

URL_REGEX = re.compile(r"(?:https?://)?(?:\S+\.)+(?:[^/]+/)+(?P<url_end>[^?/]+)")

def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f)

def absolute_extension_determination(url):
    """
    Making use of the best regular expression I've ever seen.
    """
    match = URL_REGEX.search(url)
    if match:
        url_end = match.group('url_end')
        return '' if url_end.rfind('.') == -1 else url_end[url_end.rfind('.') + 1:]
    return ''

def single_threaded_download(url, _path, tqdm_bar_init, headers):
    session = requests.Session()
    verify = headers.pop('ssl_verification', True)
    response_headers = session.head(url, allow_redirects=True, verify=verify, headers=headers)
    content_length = int(response_headers.headers.get('content-length') or 0)    
    tqdm_bar = tqdm_bar_init(content_length)
    
    with open(_path, 'ab') as sw:
        d = sw.tell()
        tqdm_bar.update(d)
        while content_length > d:
            try:
                for chunks in session.get(url, allow_redirects=True, stream=True, headers={'Range': 'bytes=%d-' % d, **(headers or {})}, verify=verify, timeout=3).iter_content(0x4000):
                    size = len(chunks)
                    d += size
                    tqdm_bar.update(size)
                    sw.write(chunks)
            except requests.RequestException as e:
                """
                A delay to avoid rate-limit(s).
                """
                print("[\x1b[31manimdl-download-exception\x1b[39m] {}".format('Downloading error due to "{!r}", retrying.'.format(e)))
                time.sleep(AUTO_RETRY)
    tqdm_bar.close()

def hls_download(quality_dict, _path, episode_identifier, _tqdm=True, preferred_quality=QUALITY):
    
    session = requests.Session()
    _tqdm_bar = None
    
    with open(_path, 'ab') as sw:
        for content in hls_yield(session, quality_dict, preferred_quality=preferred_quality):
            if _tqdm and not _tqdm_bar:
                _tqdm_bar = tqdm(desc="[HLS] %s " % episode_identifier, total=content.get('total', 0), unit='ts')
            sw.write(content.get('bytes'))
            if _tqdm:
                _tqdm_bar.update(1)
            
    if _tqdm:
        _tqdm_bar.close()