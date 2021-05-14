import json
from pathlib import Path

from ..associator import Associator

session_dict_example = {
    'anime_url': 'https://twist.moe/a/one-piece/',
    'afl': {
        'url': 'https://animefillerlist.com/shows/one-piece',
        'offset': 0,
        'canon': True,
        'mixed_canon': True,
        'fillers': False,
    },
    'start': 1,
    'end': None,
    'current': 1,
}

def unpack_afl_config(afl_config):
    """
    Unpacks to: (url, offset, canon, mixed_canon, fillers)
    """
    if not afl_config:
        return None, 0, True, True, True

    return afl_config.get('url', None), \
        afl_config.get('offset', 0), \
        afl_config.get('canon', True), \
        afl_config.get('mixed_canon', True), \
        afl_config.get('fillers', True), \

class AnimDLCliObject(object):
    """
    Any objects associated with the AnimDL cli must inherit this class.
    """

class AnimDLSession(AnimDLCliObject):
    """
    A session with AnimDL.
    
    Basically added so that you can continue watching your anime where you've left it.
    """
    
    def __init__(self, session_file):
        
        self.session_file = Path(session_file)
        
        if self.session_file.exists() and self.session_file.is_file():
            with open(self.session_file, 'r') as sf:
                self.previous_session = json.load(sf)
        else:
            self.previous_session = {}
            with open(self.session_file, 'w') as sfw:
                sfw.write('{}')

    def get_session_generator(self):
        
        afl_url, offset, canon, mixed_canon, fillers = unpack_afl_config(self.previous_session.get('afl', {}))
        associator = Associator(self.previous_session.get('anime_url'), afl_url)
        
        return associator.fetch_appropriate(
            self.previous_session.get('current', 1) or 1,
            self.previous_session.get('end', None) or None,
            offset=offset,
            canon=canon,
            mixed_canon=mixed_canon,
            fillers=fillers,
        )
        
    def update_session(self, current_episode):
        self.previous_session.update({'current': current_episode})
        
        with open(self.session_file, 'w') as sfw:
            json.dump(self.previous_session, sfw)
            
    @classmethod
    def create_new_session(cls, session_file, url, afl_config, start, end):
        with open(session_file, 'w') as sfw:
            json.dump(
                {
                    'anime_url': url,
                    'afl': afl_config,
                    'start': start,
                    'end': end,
                    'current': start,
                },
                sfw
            )

        return cls(session_file)


    @staticmethod
    def session_evaluator(session_dict):
        
        if not session_dict:
            return "Unable to continue from previous session as there was none. (Your session file may have gotten deleted.)", False
        
        remarks = ("The previous session indicates scraping from '%(anime_url)s' and " + 
            (" was set to continue to the end from E%(start)02d" if not session_dict.get('end') else " was set to play from E%(start)02d-E%(end)02d. ") + 
                "Currently the session has reached E%(current)02d.") % session_dict
        
        if session_dict.get('afl'):
            remarks += "Filler list from %(url)s with offset of %(offset)s was set. The filter for the session was set to [Canon: %(canon)s, Mixed Canon/Filler: %(mixed_canon)s, Filler: %(fillers)s]."
            
        return remarks, True
