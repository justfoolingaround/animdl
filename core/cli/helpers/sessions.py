"""
Helper functions to do session file handling with ease.
"""
import json
from pathlib import Path

from ...config import QUALITY


def load_sessions(session_file):
    if not Path(session_file).exists():
        return []
    
    with open(session_file, 'r') as sl:
        return json.load(sl)
    
def generate_download_arguments(session_dict):

    fl = session_dict.get('afl', {})

    return {
        'query': session_dict.get('url', ''),
        'anonymous': False,
        'start': session_dict.get('start', 1),
        'end': session_dict.get('end', 0),
        'title': session_dict.get('identifier', ''),
        'filler_list': fl.get('url', ''),
        'offset': fl.get('offset', 0),
        'filler': fl.get('allow-filler', False),
        'mixed': fl.get('allow-mixed', False),
        'canon': fl.get('allow-canon', False),
        'idm': session_dict.get('idm', False),
        'auto': False,
        'index': 0,
        'quiet': False,
        'quality': QUALITY
    }

def generate_stream_arguments(session_dict):
    download_args = generate_download_arguments(session_dict)
    download_args.pop('end', '')
    download_args.pop('idm', '')
    download_args.pop('quality', '')
    return {**download_args, 'player_opts': [], 'mpv': True, 'vlc': False}

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
                    'allow-filler': afl_fillers,
                    'allow-canon': afl_canon,
                    'allow-mixed': afl_mixed,
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
                        'allow-filler': afl_fillers,
                        'allow-canon': afl_canon,
                        'allow-mixed': afl_mixed,
                    }
                }
        )
        
def describe_session_dict(session_dict):
    initial = session_dict.get('identifier')
    
    if session_dict.get('type') == 'download':
        initial += " [Downloading" + " using IDM]" if session_dict.get('idm') else ']'
    
    end = session_dict.get('end')
    initial += " [{}/{}]".format(session_dict.get('start'), end if isinstance(end, int) else '?')
    
    afl = session_dict.get('afl')
    
    if afl.get('url'):
        initial += " [AFL: {url} with an offset of {offset} and filters set as filler: {}, canon: {}, mixed filler/canon: {}".format_map(afl)
        
    return initial
