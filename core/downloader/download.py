from pathlib import Path

import requests
from tqdm import tqdm


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
        
        c = b''
        
        for chunks in requests.get(url, stream=True).iter_content(0x4000):
            progress.update(len(chunks))
            c += chunks
        
        with open(base / Path('E%02d - %s.mp4' % (episode.number, episode.name)), 'wb') as sw:
            sw.write(c)