"""
This is an interactive cli which will allow you to download / watch your favorite anime without any .env hassle.

Currently, only utilizing animixplay.to.
"""

import logging
import re
import shutil

from PyInquirer import prompt

from core import *
from core.providers import animixplay

streaming_feature = True

ANIMIXPLAY = re.compile(r'^(?:https?://)?(?:\S+\.)?animixplay\.to/v1/([^?&/]+)')

def ask(message, *choices):
    return prompt([{'type': 'list', 'name': 'choice', 'message': message, 'choices': choices}]).get('choice')

def yesnoqn(message):
    return ask(message, 'Y', 'N') == 'Y'

def process_query(query):
    
    if ANIMIXPLAY.match(query):
        return query
    
    results = animixplay.animix_search(query)
    
    if not results:
        return
    
    return "https://animixplay.to%s" % ask("Found a total of %d results:" % len(results), *[{'name': title, 'value': (slug)} for slug, title, image in results])

def intinput(message, *, default=0):
    return int(ch) if (ch := input(message)).isdigit() else default

def get_afl_config():
    
    return {
        'url': input('AnimeFillerList URL :'),
        'fillers': yesnoqn('Select Fillers?'),
        'canon': yesnoqn('Select Canon?'),
        'mixed_canon': yesnoqn('Select Mixed Canon and Fillers?'),
        'offset': intinput('Offset (if the Episode 1 of your anime is marked as Episode 201 in AnimeFillerList, type in 200 (the difference); if not, type in 0 or something that\'s not an integer): '),
    }
    
def download(query, afl_config):
    
    client = Anime(
        uri=query,
        afl_uri=afl_config.pop('url'),
    )
    return internal_download(ANIMIXPLAY.match(query).group(1), client.fetch_appropriate(**afl_config))

def stream(query, afl_config):
    print("Streaming is not available currently, streaming support with mpv will be added soon (a modified version of mpv which is exclusive to AnimDL users (with features like 'SKIP INTRO') is being developed.)\nPlease bear with us, don't worry, you're being redirected to the download.")
    return download(query, afl_config)
    

def __cli__():
    
    mode = 'download'
    afl_config = {}
    
    if not shutil.which('mpv'):
        print("mpv wasn't found; streaming has been disabled.")
        streaming_feature = False
        
    if streaming_feature:
        mode = ask('Download or stream?', "download", "stream")
        
    if not (result := process_query(input('Search query: '))):
        return print("Couldn't find anything of that query.")
    
    
    if yesnoqn('Would you like to configure AnimeFillerList for filtering fillers?'):
        afl_config = get_afl_config()
        
    afl_config.update(
        {
            'start': intinput('Start from (if you want to download from Episode 12, type in 12): ') or None,
            'end': intinput('Till (if you want to download till Episode 31, type in 31, if you want to download till the end, type in 0 or something that\'s not an integer): ') or None,
         }
    )
    
    if mode == 'download':
        return download(result, afl_config)
    
    return stream(result, afl_config)
    
if __name__ == '__main__':
    __cli__()