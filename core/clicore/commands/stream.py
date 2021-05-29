from core.clicore.helpers import sfhandler
import subprocess

import click
import requests
import json

from ... import Associator
from ...animefillerlist import get_filler_list
from ..helpers import *
from .constants import SESSION_FILE

def quality_prompt(stream_list, provider):
    ts = lambda x: to_stdout(x, "%s-url-selector" % provider)
    ts("Found %d stream(s)" % len(stream_list))
    for n, anime in enumerate(stream_list, 1):
        ts("[#%02d] %s" % (n, stream_judiciary(anime.get('stream_url'))))
    
    index = click.prompt("Select by the index (defaults to 1)", default=1, type=int, show_default=False) - 1
    
    if (index + 1) > len(stream_list):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(stream_list) + 1))
        index %= len(stream_list)
    
    return stream_list[index]

@click.command(name='stream', help="Stream your favorite anime by query.")
@click.option('-q', '--query', help="A search query or anime url string to begin scraping from.", required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the streaming from.", required=False, default=0, show_default=False, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL.", required=False, default='', show_default=False)
@click.option('-fl', '--filler-list', help="Filler list associated with the content enqueued for the stream.", required=False, default='', show_default=False)
@click.option('-o', '--offset', help="Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 26s).", required=False, default=0, show_default=False)
@click.option('--filler', is_flag=True, default=True, help="Auto-skip fillers (If filler list is configured).")
@click.option('--mixed', is_flag=True, default=True, help="Auto-skip mixed fillers/canons (If filler list is configured).")
@click.option('--canon', is_flag=True, default=True, help="Auto-skip canons (If filler list is configured).")
def animdl_stream(query, start, title, filler_list, offset, filler, mixed, canon):
    """
    Streamer call for animdl streaming session.
    """    
    session = requests.Session()
    
    anime, provider = process_query(session, query)
    ts = lambda x: to_stdout(x, 'animdl-%s-streamer-core' % provider)
    tx = lambda x: to_stdout(x, 'animdl-protip')
    ts('Now initiating your stream session')
    content_name = title or anime.get('name') or ("direct-uri: %s" % query)
    if not start:
        start = click.prompt("Episode number to intiate streaming from (defaults to 1)", default=1, show_default=False) or 1
    ts("Starting stream session @ [%02d/?]" % start)
    url = anime.get('anime_url')
    anime_associator = Associator(url)    
    check = lambda *args, **kwargs: True
    raw_episodes = []
    
    if filler_list:
        raw_episodes = get_filler_list(session, filler_list, fillers=True)
        ts("Succesfully loaded the filler list from '%s'." % filler_list)
        start += offset
        check = (lambda x: raw_episodes[offset + x - 1].content_type in ((['Filler'] if filler else []) + (['Mixed Canon/Filler'] if mixed else []) + (['Anime Canon', 'Manga Canon'] if canon else [])))
       
    sfhandler.save_session(SESSION_FILE, url, start, content_name, filler_list, offset, filler, mixed, canon)
    
    for stream_urls, c in anime_associator.raw_fetch_using_check(lambda x: check(x) and x >= start):
        ts("Active stream session @ [%02d/%s]" % (c, ('%02d' % len(raw_episodes)) if raw_episodes else '?'))
        sfhandler.save_session(SESSION_FILE, url, c, content_name, filler_list, offset, filler, mixed, canon)
        playing = True
        while playing:
            title = "Episode %02d" % c
            if raw_episodes:
                title += ": %s" % raw_episodes[c - 1].title
            
            if not stream_urls:
                ts("Could not find any streams for %s." % title)
                playing = False
                continue
            
            selection = quality_prompt(stream_urls, provider) if len(stream_urls) > 1 else stream_urls[0]
            headers = selection.get('headers', {})
            _ = headers.pop('ssl_verification', True)
            mpv_process = subprocess.Popen(['mpv', selection.get('stream_url'), "--title=%s" % title] + (['--http-header-fields=%s' % ','.join('%s:%s' % (k, v) for k, v in headers.items())] if headers else []))
            mpv_process.wait()
            
            playing = False
            
            if mpv_process.returncode:
                ts("Detected a non-zero return code.")
                tx("If there was an error or a crash during playback. Don't sweat it, you're going to be prompted for this instance.")
                playing = click.confirm("[\x1b[33m%s\x1b[39m] Would you like to repeat '%s'? " % ('animdl-%s-streamer-core' % provider, title))