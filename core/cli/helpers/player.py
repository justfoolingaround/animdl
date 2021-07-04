import shutil
import subprocess
from pathlib import Path

from ...config import PLAYERS


def supported_streamers():
    for player, player_info in PLAYERS.items():
        if Path(player_info.get('executable')).exists() or shutil.which(player_info.get('executable')):
            yield player
            
def start_streaming_mpv(executable, stream_url, opts, *, headers=None, **kwargs):
    args = [executable, stream_url, '--force-window=immediate'] + (opts or [])
    
    if headers:
        args.append('--http-header-fields=%s' % '\r\n'.join('{}:{}'.format(k, v) for k, v in headers.items()))        

    content_title = kwargs.pop('content_title', '')
    
    if content_title:
        args.append('--title=%s' % content_title)
        
    return subprocess.Popen(args)

def start_streaming_vlc(executable, stream_url, opts, *, headers=None, **kwargs):
    args = [executable, stream_url] + (opts or [])
    
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

def handle_streamer(player_opts, **kwargs):
    supported = [*supported_streamers()]
    user_selection = [k for k, v in kwargs.items() if v and k in supported]    

    if not user_selection:
        return -107977

    player = user_selection.pop(0)
    player_info = PLAYERS.get(player, {})
    return lambda *a, **k: start_streaming(player, player_info.get('executable'), opts=player_info.get('opts', []) + (player_opts or []), *a, **k)

def start_streaming(player, executable, stream_url, *, headers=None, **kwargs):
    return PLAYER_MAPPING.get(player, lambda *args, **kwargs: False)(executable, stream_url, headers=headers, **kwargs)