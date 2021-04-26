import re

from .helper import *
from .animefillerlist import *
from .providers import \
    (animixplay, twistmoe)

class AnimDL:
    """
    All the AnimDL objects will inherit from this class.
    """
    
class Anime(AnimDL):
    
    def __init__(self, uri, afl_uri=None):
        
        self.url = uri
        self.filler_list = afl_uri
        
    def episode_yielder(self, urls, episode_list, offset, download_headers):
        
        if not episode_list:
            for i, url in enumerate(urls, 1):
                yield Episode(i, 'Unloaded', 'Manga Canon', '1970-01-01', url, download_headers)
            return

        for episode, url in zip(episode_list, urls):
            yield Episode(episode.number - offset, episode.title, episode.content_type, episode.aired_date, url, download_headers)
        
    def get_filler_list(self, canon=True, mixed_canon=True, fillers=False):
        
        if not self.filler_list:
            return []
        
        if not any((canon, mixed_canon, fillers)):
            raise ValueError('All the filler settings cannot be set to False.')
        
        initial_xpath = []
        
        if canon:
            initial_xpath.append("//tr[@class='manga_canon even'] | //tr[@class='manga_canon odd'] | //tr[@class='anime_canon even'] | //tr[@class='anime_canon odd']")
            
        if mixed_canon:
            initial_xpath.append("//tr[@class='mixed_canon/filler even'] | //tr[@class='mixed_canon/filler odd']")
                
        if fillers:
            initial_xpath.append("//tr[@class='filler even'] | //tr[@class='filler odd']")
        
        return get_using_xpath(self.filler_list, ' | '.join(initial_xpath))
        
    def fetch_episodes_using_animix(self, episode_list=[], *, offset=0):      
        yield from self.episode_yielder(animixplay.get_parser(self.url)(animixplay.from_site_url(self.url), check=construct_check(episode_list, offset)), episode_list, offset, download_headers={})
            
    def fetch_episodes_using_twistmoe(self, episode_list=[], *, offset=0):
        
        check = construct_check(episode_list, offset)
        yield from self.episode_yielder([a.get('stream_url') for i, a in enumerate(twistmoe.get_twistmoe_anime_uri(twistmoe.TWIST_URL_RE.match(self.url).group(1)), 1) if check(i)], episode_list, offset, download_headers={'referer': 'https://twist.moe/'})
            
    def fetch_appropriate(self, start=None, end=None, *, 
        offset=0, canon=True, mixed_canon=True, fillers=False):

        if not any((canon, mixed_canon, fillers)):
            return
        
        AVAILABLE_FETCHERS = {
            'animix': {
                'matcher': re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v1/([^?&/]+)'),
                'fetcher': self.fetch_episodes_using_animix,
            },
            'twistmoe': {
                'matcher': twistmoe.TWIST_URL_RE,
                'fetcher': self.fetch_episodes_using_twistmoe,
            }
        }
        
        for fetcher, data in AVAILABLE_FETCHERS.items():
            if data.get('matcher').match(self.url):
                yield from data.get('fetcher', lambda *args, **kwargs: None)(episode_list=[*filter_episodes(self.get_filler_list(canon, mixed_canon, fillers), start=start, end=end, offset=offset)], offset=offset or 0)
                break
            
class Episode(AnimDL):
    
    def __init__(self, number, name, filler,
            date_aired, urls, download_headers):
        self.number = number
        self.name = name
        self.filler = filler
        self.date_aired = date_aired
        self.urls = urls if not isinstance(urls, str) else (urls,)
        self.download_headers = download_headers
    
    @property
    def is_filler(self):
        return self.filler == 'Filler'
    
    @property
    def is_canon(self):
        return self.filler in ['Anime Canon', 'Manga Canon']
    
    @property
    def is_mixed(self):
        return not (self.is_filler and self.is_canon)
    
    def get_url(self, ext='mp4'):
        for urls in self.urls:
            if urls.endswith(ext):
                return urls
        
    def __repr__(self):
        return "< Episode %02d - '%s' [%s], %s >" % (self.number, self.name, self.filler, self.date_aired)