"""
This is an interactive cli which will allow you to download / watch your favorite anime without any .env hassle.
"""

import shutil
import subprocess

from PyInquirer import prompt

from core import internal_download
from core.helper.cli_helper import AnimDLSession
from core.providers import animixplay, current_providers

SESSION_FILE = "animdl_session.json"

streaming_feature = bool(shutil.which('mpv'))

def ask(message, *choices):
    return prompt([{'type': 'list', 'name': 'choice', 'message': message, 'choices': choices}]).get('choice')

def yesnoqn(message):
    return ask(message, 'Y', 'N') == 'Y'

def process_query(query):

    for content, data in current_providers.items():
        if data.get('matcher').search(query):
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
    
def stream(session, shaders=None):
    
    for episode in session.get_session_generator():
        
        replay = True
        while replay:
            session.update_session(episode.number)
            print("Now playing: Episode %02d - '%s'" % (episode.number, episode.name))
            
            quality = ask('There seems to be multiple qualities available, please pick a quality to start streaming.', *episode.qualities) if [*episode.qualities][1:] else [*episode.qualities][0]
            stream_url, headers = episode.get_url(quality)
            process = subprocess.Popen(['mpv', stream_url, "--title=Episode %02d - %s" % (episode.number, episode.name)] + (['--http-header-fields=%s' % ','.join('%s:%s' % (k, v) for k, v in headers.items())] if headers else []) + (['--glsl-shaders=%s' % shaders] if shaders else []))
            process.wait()
        
            choice = ask('AnimDL detects that the process has ended, would you like to view the next episode in the queue or replay this one?', 'Next', 'Replay')
            if choice == 'Next':
                replay = False

def __cli__():
    
    mode = 'download'
    afl_config = {}
    
    if not streaming_feature:
        print("mpv wasn't found; streaming has been disabled.")
        
    if streaming_feature:
        mode = ask('Download or stream?', "download", "stream")
        
    session = AnimDLSession(SESSION_FILE)
    
    if session.previous_session and yesnoqn('Session data from previous session found, would you like to continue from it?'):
        remarks, _ = session.session_evaluator(session.previous_session)
        print(remarks)
        
    else:
        if not (result := process_query(input('Search query: '))):
            return print("Couldn't find anything of that query.")
        
        if yesnoqn('Would you like to configure AnimeFillerList for filtering fillers?'):
            afl_config = get_afl_config()
        session = session.create_new_session(SESSION_FILE, result, afl_config, intinput('Start from (if you want to {0} from Episode 12, type in 12): '.format(mode)) or None, intinput('Till (if you want to {0} till Episode 31, type in 31, if you want to {0} till the end, type in 0 or something that\'s not an integer): '.format(mode)) or None,)
        
    if mode == 'stream':
        shaders = input("Upscaling shader: (Leave blank if you don't know what this is for)") or None        
        return stream(session, shaders)

    return internal_download(input('Download folder name (might want to make it something reasonable like "One Piece"): '), session.get_session_generator())
    
if __name__ == '__main__':
    __cli__()