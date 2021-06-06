import re
import time
from pathlib import Path

import requests
from tqdm import tqdm

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

def generate_appropriate_header(url, *, headers, verify):
    """
    Combat against annoying responses that contain location in the headers but \
        doesn't redirect properly.
    """
    c = requests.head(url, headers=headers, verify=verify)
    semi_url = c.headers.get('location')
    while semi_url:
        c = requests.head(semi_url, headers=headers, verify=verify)
        semi_url = c.headers.get('location')
    return c.headers, semi_url or url

def _download(url, _path, tqdm_bar_init, headers):
    
    verify = headers.pop('ssl_verification', True)
    header, url = generate_appropriate_header(url, headers=headers, verify=verify)
    
    r = int(header.get('content-length', 0) or 0)    
    d = 0
    
    tqdm_bar = tqdm_bar_init(r)
    
    with open(_path, 'ab') as sw:
        d = sw.tell()
        tqdm_bar.update(d)
        while r > d:
            try:
                for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % d, **(headers or {})}, verify=verify).iter_content(0x4000):
                    size = len(chunks)
                    d += size
                    tqdm_bar.update(size)
                    sw.write(chunks)
            except requests.RequestException:
                """
                A delay to avoid rate-limit(s).
                """
                time.sleep(.3)
            
    tqdm_bar.close()

def internal_download_v1(base_folder, episodes):
    """
    Toss a list of Episodes (fetch those from the Anime class or construct it yourself.)
    """
    base = Path('./%s/' % sanitize_filename(base_folder))
    base.mkdir(exist_ok=True)
    
    for episode in episodes:
        url = episode.get_url()
        
        if not url:
            continue
        
        r = int(requests.head(url).headers.get('content-length', 0))        
        progress = tqdm(desc='Episode %02d, %s' % (episode.number, episode.name), total=r, unit='B', unit_scale=True, unit_divisor=1024)
        
        with open(base / (Path('E%02d - %s.mp4' % (episode.number, sanitize_filename(episode.name)))), 'ab') as sw:
            offset = sw.tell()
            
            if offset == r:
                progress.close()
                continue
            
            for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % offset}).iter_content(0x4000):
                progress.update(len(chunks))
                sw.write(chunks)
                
        progress.close()
        
def hls_download(quality_dict, _path, episode_identifier, _tqdm=True):
    
    session = requests.Session()
    _tqdm_bar = None
    
    with open(_path, 'ab') as sw:
        for content in hls_yield(session, quality_dict):
            if _tqdm and not _tqdm_bar:
                _tqdm_bar = tqdm(desc="[HLS] %s " % episode_identifier, total=content.get('total', 0), unit='ts')
            sw.write(content.get('bytes'))
            if _tqdm:
                _tqdm_bar.update(1)
            
    if _tqdm:
        _tqdm_bar.close()
    
        
def internal_download(base_folder, episodes):
    """
    v2, currently being used.
    """
    base = Path('./%s/' % sanitize_filename(base_folder))
    base.mkdir(exist_ok=True)
    
    for episode in episodes:
        url, headers = episode.get_url()
        extension = absolute_extension_determination(url or '')
        
        identifier = "Episode {0.number:02d}, {0.name}".format(episode)
        
        if extension in ['m3u8', 'm3u']:
            hls_download(episode.urls, base / (Path('E%02d - %s.ts' % (episode.number, sanitize_filename(episode.name)))), identifier)
            continue

        if not url:
            continue
        
        _download(url, base / (Path('E%02d - %s.%s' % (episode.number, sanitize_filename(episode.name), extension))), lambda r: tqdm(desc='Episode %02d, %s' % (episode.number, episode.name), total=r, unit='B', unit_scale=True, unit_divisor=1024), headers)