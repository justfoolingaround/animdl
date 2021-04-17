from pathlib import Path

import requests
from tqdm import tqdm

def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f)

def generate_appropriate_header(url):
    
    c = requests.head(url)
    while semi_url := c.headers.get('location'):
        c = requests.head(semi_url)
    return c.headers, semi_url or url

def _download(url, _path, tqdm_bar_init, headers):
    
    header, url = generate_appropriate_header(url)
    
    r = int(header.get('content-length', 0) or 0)    
    d = 0
    
    tqdm_bar = tqdm_bar_init(r)
    
    with open(_path, 'ab') as sw:
        while r != d:
            d = sw.tell()
            tqdm_bar.update(d)
            
            if r == d:
                break
            
            try:
                for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % d}, headers=headers).iter_content(0x4000):
                    size = len(chunks)
                    d += size
                    tqdm_bar.update(size)
                    sw.write(chunks)
            except requests.RequestException:
                pass
            
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
        
def internal_download(base_folder, episodes, *, headers={}):
    """
    v2, currently being used.
    """
    base = Path('./%s/' % sanitize_filename(base_folder))
    base.mkdir(exist_ok=True)
    
    for episode in episodes:
        url = episode.get_url()
        
        if not url:
            continue
        
        _download(url, base / (Path('E%02d - %s.mp4' % (episode.number, sanitize_filename(episode.name)))), lambda r: tqdm(desc='Episode %02d, %s' % (episode.number, episode.name), total=r, unit='B', unit_scale=True), headers)