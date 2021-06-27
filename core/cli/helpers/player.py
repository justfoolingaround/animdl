import subprocess
from rich import print
from ...config import PLAYER_EXECUTABLE

def start_streaming(stream_url, *, headers=None, window_title=None):
    if PLAYER_EXECUTABLE == 'mpv':
        args = [PLAYER_EXECUTABLE, stream_url, '--force-window=immediate']
        if headers:
            args.append('--http-header-fields=%s' % '\r\n'.join('{}:{}'.format(k, v) for k, v in headers.items()))
            
        if window_title:
            args.append('--title=%s' % window_title)
    elif PLAYER_EXECUTABLE == 'vlc':
        args = [PLAYER_EXECUTABLE, f'{stream_url}']
    else:
        print("[red]vlc player not on PATH or environment not refreshed,type refreshenv in cmd and run animdl again.\nFor adding a program to PATH,refer to https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/[/red]")
        exit()    
    return subprocess.Popen(args)
