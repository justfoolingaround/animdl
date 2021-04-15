from pathlib import Path

import requests
from tqdm import tqdm

def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f)

def internal_download(base_folder, episodes):
    """
    Toss a list of Episodes (fetch those from the Anime class or construct it yourself.)
    """
    base = Path('./%s/' % base_folder)
    base.mkdir()
    
    for episode in episodes:
        url = episode.get_url()
        
        if not url:
            continue
        
        r = int(requests.head(url).headers.get('content-length', 0))
        progress = tqdm(desc='Episode %02d, %s' % (episode.number, episode.name), total=r, unit='B', unit_scale=True)
        
        path_to_file = base / Path('E%02d - %s.mp4' % (episode.number, sanitize_filename(episode.name)))
        offset = 0
        
        if path_to_file.exists():
            with open(path_to_file, 'rb') as sr:
                offset = sr.tell()
        
        progress.update(offset)
        
        with open(path_to_file, 'wb') as sw:
            sw.seek(offset)
            for chunks in requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % offset}).iter_content(0x4000):
                progress.update(len(chunks))
                sw.write(chunks)