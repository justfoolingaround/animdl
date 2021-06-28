import shutil
import subprocess
from pathlib import Path

from ...config import PLAYERS


def supported_streamers():
    for player, path in PLAYERS.items():
        if Path(path).exists() or shutil.which(path):
            yield player
            
def start_streaming_mpv(executable, stream_url, *, headers=None, **kwargs):
    args = [executable, stream_url, '--force-window=immediate']
    
    if headers:
        args.append('--http-header-fields=%s' % '\r\n'.join('{}:{}'.format(k, v) for k, v in headers.items()))        

    content_title = kwargs.pop('content_title', '')
    
    if content_title:
        args.append('--title=%s' % content_title)
        
    return subprocess.Popen(args)

def start_streaming_vlc(executable, stream_url, *, headers=None, **kwargs):
    args = [executable, stream_url]
    
    if headers:
        if headers.get('referer'):
            args.append('--http-referrer={}'.format(headers.get('referer')))
        
        if headers.get('user-agent'):
            args.append('--http-user-agent={}'.format(headers.get('user-agent')))
    
    return subprocess.Popen(args)

PLAYER_MAPPING = {
    'mpv': start_streaming_mpv,
    'vlc': start_streaming_vlc,
}

def handle_streamer(**kwargs):
    supported = [*supported_streamers()]
    user_selection = [k for k, v in kwargs.items() if v and k in supported]    

    if not user_selection:
        return -107977

    player = user_selection.pop(0)
    return lambda *a, **k: start_streaming(player, PLAYERS.get(player), *a, **k)

def start_streaming(player, executable, stream_url, *, headers=None, **kwargs):
    return PLAYER_MAPPING.get(player, lambda *args, **kwargs: False)(executable, stream_url, headers=headers, **kwargs)