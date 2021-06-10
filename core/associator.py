import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from .animefillerlist import get_filler_list
from .classes import AnimDLObject, Episode
from .helper import append_protocol, construct_check, filter_episodes
from .providers import get_appropriate


class Associator(AnimDLObject):
    """
    Associator associates a anime with its url, filler list and stream url.
    """
    
    def __init__(self, uri, afl_uri=None, *, session=None):
        
        self.url = append_protocol(uri)
        self.filler_list = afl_uri
        
        self.session = session or requests.Session()
                
    def fetch_appropriate(self, start=None, end=None, *, 
        offset=0, canon=True, mixed_canon=True, fillers=False):

        if not any((canon, mixed_canon, fillers)):
            return
        
        episode_list = []
        check = lambda n: ((start or 1) + offset) <= n <= ((end or float('inf')) + offset)
        
        if self.filler_list:
            episode_list = [*filter_episodes(get_filler_list(self.session, self.filler_list, canon, mixed_canon, fillers), start, end, offset)]
            check = construct_check(episode_list, offset)
                    
        for i, url in enumerate(get_appropriate(self.session, self.url, check=check), 1):
            if episode_list:
                e = episode_list.pop(0)
                yield Episode(e.number - offset, e.title, e.content_type, e.aired_date, url[0]())
            else:
                yield Episode.unloaded(i + start - 1 - offset, url[0]())

    def raw_fetch_using_check(self, check):
        yield from get_appropriate(self.session, self.url, check=check)