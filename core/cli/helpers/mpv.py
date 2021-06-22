import subprocess

from ...config import MPV_EXECUTABLE

def start_streaming(stream_url, *, headers=None, window_title=None):
    
    args = [MPV_EXECUTABLE, stream_url, '--force-window=immediate']
    if headers:
        args.append('--http-header-fields=%s' % '\r\n'.join('{}:{}'.format(k, v) for k, v in headers.items()))
        
    if window_title:
        args.append('--title=%s' % window_title)
    
    return subprocess.Popen(args)