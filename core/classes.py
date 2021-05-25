from .helper import *

class AnimDLObject(object):
    """
    All the AnimDL objects will inherit from this class.
    """
       
class Episode(AnimDLObject):
    
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
    
    @classmethod
    def unloaded(cls, episode_number, urls):
        return cls(episode_number, 'Unloaded', 'Manga Canon', '1970-01-01', urls)
    
    @property
    def qualities(self):
        return {stream.get('quality') for stream in self.urls}
    
    def get_url(self, quality=None):        
        for urls in self.urls:
            if (not quality) or (urls.get('quality') == quality):
                return urls.get('stream_url', ''), urls.get('headers', {})
        return None, None
        
    def __repr__(self):
        return "< Episode %02d - '%s' [%s], %s >" % (self.number, self.name, self.filler, self.date_aired)