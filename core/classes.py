from .animefillerlist import *
from .animixplay.stream_url import *

class AnimDL:
    """
    All the AnimDL objects will inherit from this class.
    """
    
class Anime(AnimDL):
    def __init__(self, animix_uri, afl_uri=None):
        
        self.url = animix_uri
        self.filler_list = afl_uri
        
    def fetch_episodes(self, start=None, end=None, *, 
        offset=0, canon=True, mixed_canon=True,fillers=False):
        """
        An appropriate constructor for the episodes class.
        
        The purpose of the `offset` parameter is to solve the problems in downloading multi-seasoned anime that might be listed as one in AnimeFillerList but different in the anime site.
        
        In the case of Fairy Tail, the url (non-anime filler list one) can reference to the second season and the offset can be 175.
        """
        if not any((canon, mixed_canon, fillers)):
            return
        
        initial_xpath = []
        
        if canon:
            initial_xpath.append("//tr[@class='manga_canon even'] | //tr[@class='manga_canon odd'] | //tr[@class='anime_canon even'] | //tr[@class='anime_canon odd']")
            
        if mixed_canon:
            initial_xpath.append("//tr[@class='mixed_canon/filler even'] | //tr[@class='mixed_canon/filler odd']")
                
        if fillers:
            initial_xpath.append("//tr[@class='filler even'] | //tr[@class='filler odd']")
        
        if not end:
            end = float('inf')
        
        if not start:
            start = 1
        
        if start > end:
            start, end = end, start
        
        URLS = get_parser(self.url)(from_site_url(self.url), check=lambda v: start <= (v + 1) <= end) # type: list[tuple]
        
        if not self.filler_list:
            for i, url in enumerate(URLS, 1):
                yield Episode(i, 'Unloaded', 'Manga Canon', '1970-01-01', url)
            return
        
        for episode_number, title, typ, date in filter(lambda x:(offset + end + 1) > x[0] > (offset + start - 1), get_using_xpath(self.filler_list, ' | '.join(initial_xpath))):
            if not URLS:
                return print('Stream URL scraper has exhausted - cannot fetch urls from %s from "E%02d, %s".' % (self.url, episode_number - offset, title))
            yield Episode(episode_number - offset, title, typ, date, URLS.pop(0))
            
class Episode(AnimDL):
    
    def __init__(self, number, name, filler,
            date_aired, urls):
        self.number = number
        self.name = name
        self.filler = filler
        self.date_aired = date_aired
        self.urls = urls
    
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