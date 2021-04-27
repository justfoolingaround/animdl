from .helper import *

class AnimDLObject(object):
    """
    All the AnimDL objects will inherit from this class.
    """
       
class Episode(AnimDLObject):
    
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
    
    @classmethod
    def unloaded(cls, episode_number, urls, download_headers):
        return cls(episode_number, 'Unloaded', 'Manga Canon', '1970-01-01', urls, download_headers)
    
    def get_url(self, ext='mp4'):
        for urls in self.urls:
            if urls.endswith(ext):
                return urls
        
    def __repr__(self):
        return "< Episode %02d - '%s' [%s], %s >" % (self.number, self.name, self.filler, self.date_aired)