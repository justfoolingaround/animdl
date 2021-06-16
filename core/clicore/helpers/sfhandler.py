"""
Helper functions to do session file handling with ease.
"""
import json
from pathlib import Path

SESSION_FILE_TEMPLATE = [{
    'identifer': 'one piece',
    'url': 'https://9anime.to/watch/one-piece.ov8',
    'type': 'download',
    'start': 1,
    'end': None,
    'afl': {
        'offset': 0,
        'url': 'https://animefillerlist.com/shows/one-piece',
        'autoskip-filler': False,
        'autoskip-canon': False,
        'autoskip-mixed': False,
    }
}]


def load_sessions(session_file):
    if not Path(session_file).exists():
        return []
    
    with open(session_file, 'r') as sl:
        return json.load(sl)
    
def generate_download_arguments(session_dict):
    return (session_dict.get('url', ''), 
            session_dict.get('start', 1), 
            session_dict.get('end', 0), 
            session_dict.get('identifier', ''), 
            session_dict.get('idm', False), 
            session_dict.get('afl', {}).get('url', ''),
            session_dict.get('afl', {}).get('offset', 0),
            session_dict.get('afl', {}).get('autoskip-filler', False),
            session_dict.get('afl', {}).get('autoskip-canon', False),
            session_dict.get('afl', {}).get('autoskip-mixed', False),            
            )

def generate_stream_arguments(session_dict):
    u, s, e, i, idm, au, ao, af, ac, am = generate_download_arguments(session_dict)
    return u, s, i, au, ao, af, ac, am

def search_identifiers(session_file, identifer):
    for session in load_sessions(session_file):
        if identifer.lower() in session.get('identifier', '').lower():
            yield session
        
def get_most_recent_session(session_file):
    sessions = load_sessions(session_file)
    return sessions.pop() if sessions else {}

def update_session_file(session_file, session_dict):
    if not Path(session_file).exists():
        with open(session_file, 'w') as sf:
            json.dump([], sf, indent=4)

    sessions = load_sessions(session_file)
    with open(session_file, 'w') as sw:
        json.dump([s for s in sessions if (s.get('identifier', '')).lower() != session_dict.get('identifier', '').lower()] + [session_dict], sw, indent=4)
        

def save_session(session_file, url, start, identifier, afl_url, afl_offset, afl_fillers, afl_canon, afl_mixed, *, t='stream', end=0, idm=False):
    
    if t == 'stream':
        return update_session_file(
            session_file,
            {
                'url': url,
                'identifier': identifier.lower(),
                'start': start,
                'type': 'stream',
                'afl': {
                    'offset': afl_offset,
                    'url': afl_url,
                    'autoskip-filler': afl_fillers,
                    'autoskip-canon': afl_canon,
                    'autoskip-mixed': afl_mixed,
                }
            }
        )
        
    if t == 'download':
        return update_session_file(
            session_file,
                {
                    'url': url,
                    'identifier': identifier.lower(),
                    'start': start,
                    'end': end,
                    'type': 'download',
                    'idm': idm,
                    'afl': {
                        'offset': afl_offset,
                        'url': afl_url,
                        'autoskip-filler': afl_fillers,
                        'autoskip-canon': afl_canon,
                        'autoskip-mixed': afl_mixed,
                    }
                }
        )
        
def describe_session_dict(session_dict):
    
    end = '?' if not isinstance(session_dict.get('end'), int) else '{:02d}'.format(session_dict.get('end'))    
    initial = "\x1b[35m{type}\x1b[39m@{identifier}, active scraping from \x1b[91m{url}\x1b[39m @ [{start:02d}/{end}]".format_map({**session_dict, 'end': end})
    
    if session_dict.get('afl', {}).get('url'):
        initial += "; Filler list from \x1b[91m%(url)s\x1b[39m [Offset: %(offset)s]; active filters: [F, M, C: %(autoskip-filler)s, %(autoskip-mixed)s, %(autoskip-canon)s]" % session_dict.get('afl')
        
    return initial