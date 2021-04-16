from pathlib import Path

import requests
from tqdm import tqdm

def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f)

def _download(url, _path, *, tqdm_bar=None):
    """
    *contextually untested code*; test once before direct implementation.
    
    Works in mine as the try-catch is almost untestable due to high internet speed - tests in a lower internet speed is recommended.
    
    P.S.: Tested on: >250 Mbps with twist.moe & gga urls, Requested test on: <50 Mbps with the same urls.
    
    Modified & added by Syl - 2021-04-16
    """
    r = int(requests.head(url).headers.get('content-length', 0))     
    d = 0
    
    if tqdm_bar:
        tqdm_bar.total = r
    
    
    with open(_path, 'ab') as sw:
        while r != d:
            d = sw.tell()
            
            if r == d:
                break
            
            try:
                for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % d}).iter_content(0x4000):
                    size = len(chunks)
                    d += size
                    if tqdm_bar:
                        tqdm_bar.update(size)
                    sw.write(chunks)
            except requests.RequestException:
                pass
            
    if tqdm_bar:
        tqdm_bar.close()

def internal_download(base_folder, episodes):
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
        progress = tqdm(desc='Episode %02d, %s' % (episode.number, episode.name), total=r, unit='B', unit_scale=True)
        
        with open(base / (Path('E%02d - %s.mp4' % (episode.number, sanitize_filename(episode.name)))), 'ab') as sw:
            offset = sw.tell()
            
            if offset == r:
                progress.close()
                continue
            
            for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % offset}).iter_content(0x4000):
                progress.update(len(chunks))
                sw.write(chunks)
                
        progress.close()