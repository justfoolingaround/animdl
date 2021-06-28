import json
import os
from pathlib import Path
import shutil

def merge_dicts(dict1, dict2):
    for k, v in dict1.items():
        if isinstance(v, dict):
            merge_dicts(v, dict2.setdefault(k, {}))
        else:
            if not k in dict2:
                dict2[k] = v
    return dict2
        
CONFIGURATION_FILE_PATH = Path(os.getenv('ANIMDL_CONFIG') or './animdl_config.json')

DEFAULT_CONFIG = {
    'session_file': 'cli_session_animdl.json',
    'default_provider': '9anime',
    'site_urls': {
        '4anime': 'https://4anime.to/',
        '9anime': 'https://9anime.to/',
        'anime1': 'https://www.anime1.com/',
        'animefreak': 'https://animefreak.tv/',
        'animeout': 'https://animeout.xyz/',
        'animepahe': 'https://animepahe.com/',
        'animixplay': 'https://animixplay.to/',
        'gogoanime': 'https://gogoanime.ai/',   
        'twist': 'https://twist.moe/',
    },
    'preferred_quality': 1080,
    'default_player': 'mpv',
    'players': {
        'mpv': 'mpv.exe',
        'vlc': 'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe'    
    },
    'schedule': {
        'site_url': 'https://www.livechart.me/',
        'date_format': '%b. %d, %A',
        'time_format': '%X'
    }
}

CONFIG = DEFAULT_CONFIG

if CONFIGURATION_FILE_PATH.exists():
    with open(CONFIGURATION_FILE_PATH, 'r') as conf:
        CONFIG = merge_dicts(DEFAULT_CONFIG, json.load(conf))
        
SITE_URLS = CONFIG.get('site_urls', {})

FOURANIME  = SITE_URLS.get('4anime')
NINEANIME  = SITE_URLS.get('9anime')
ANIME1     = SITE_URLS.get('anime1')
ANIMEFREAK = SITE_URLS.get('animefreak')
ANIMEOUT   = SITE_URLS.get('animeout')
ANIMEPAHE  = SITE_URLS.get('animepahe')
ANIMIXPLAY = SITE_URLS.get('animixplay')
GOGOANIME  = SITE_URLS.get('gogoanime')
TWIST      = SITE_URLS.get('twist')

QUALITY    = CONFIG.get('preferred_quality')

DEFAULT_PLAYER = CONFIG.get('default_player')
PLAYERS = CONFIG.get('players')

LIVECHART   = CONFIG.get('schedule', {}).get('site_url')

DATE_FORMAT = CONFIG.get('schedule', {}).get('date_format')
TIME_FORMAT = CONFIG.get('schedule', {}).get('time_format')

SESSION_FILE = CONFIG.get('session_file')
DEFAULT_PROVIDER = CONFIG.get('default_provider')