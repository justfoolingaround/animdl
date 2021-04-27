"""
This is an interactive cli which will allow you to download / watch your favorite anime without any .env hassle.

Currently, only utilizing animixplay.to.
"""

import re
import shutil
import subprocess

from PyInquirer import prompt

from core import *
from core.providers import animixplay

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
    
def stream(url_generator):
    
    for episode in url_generator:
        
        replay = True
        while replay:
            print("Now playing: Episode %02d - '%s'" % (episode.number, episode.name))            
            process = subprocess.Popen(['mpv', episode.get_url('m3u8') or episode.get_url(), '--http-header-fields="{}"'.format(','.join("%s: %s" % (k,v) for k,v in episode.download_headers.items())) if episode.download_headers else ''])
            process.wait()
        
            choice = ask('AnimDL detects that the process has ended, would you like to view the next episode in the queue or replay this one?', 'Next', 'Replay')
            if choice == 'Next':
                replay = False

def __cli__():
    
    streaming_feature = True
    mode = 'download'
    afl_config = {}
    
    if not shutil.which('mpv'):
        print("mpv wasn't found; streaming has been disabled.")
        streaming_feature = False
        
    if streaming_feature:
        mode = ask('Download or stream?', "download", "stream")
        
    if not (result := process_query(input('Search query: '))):
        return print("Couldn't find anything of that query.")
    
    client = Associator(result)
    
    if yesnoqn('Would you like to configure AnimeFillerList for filtering fillers?'):
        afl_config = get_afl_config()
    
    client.filler_list = afl_config.pop('url', None)

    if mode == 'stream':
        start = intinput("Start streaming from (if you want to stream from Episode 12, type in 12): ") or None
        return stream(client.fetch_appropriate(start=start, **afl_config))

    afl_config.update(
        {
            'start': intinput('Start from (if you want to download from Episode 12, type in 12): ') or None,
            'end': intinput('Till (if you want to download till Episode 31, type in 31, if you want to download till the end, type in 0 or something that\'s not an integer): ') or None,
         }
    )
    
    return internal_download(ANIMIXPLAY.match(result).group(1), client.fetch_appropriate(**afl_config))
    
if __name__ == '__main__':
    __cli__()