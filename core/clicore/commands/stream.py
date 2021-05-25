import subprocess

import click
import requests

from ... import Associator
from ...animefillerlist import get_filler_list
from ..helpers import *


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

@click.command(name='stream')
@click.option('-q', '--query', help="A search query or anime url string to begin scraping from.", required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the streaming from.", required=False, default=0, show_default=False, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL.", required=False, default='', show_default=False)
def animdl_stream(query, start=0, title=''):
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
    anime_associator = Associator(anime.get('anime_url'))    
    check = lambda *args, **kwargs: True
    raw_episodes = []
    
    tx("Load AnimeFillerList for scraping out episodes?")
    tx("AnimeFillerList allows you to get episode names, filter out filler content & aware the streamer about the index of last episode.")
    tx("A few seconds of configuring could elevate the streaming experience more.")
    
    if click.confirm("Configure AnimeFillerList settings? ", default=False):
        tx("Now configuring AnimeFillerList; please read the stdout stream below to be aware about what to enter.")
        tx("Required: AnimeFillerList URL.")
        tx("Optional: Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 27)")
        tx("Optional: Auto-skip fillers content.")
        tx("Optional: Auto-skip mixed filler/canon content.")
        tx("Optional: Auto-skip canon content.")
        afl_url = click.prompt("Filler list URL")
        raw_episodes = get_filler_list(session, afl_url, fillers=True)
        tx("Succesfully loaded the filler list from '%s'." % afl_url)
        offset = click.prompt("Content offset (defaults to 0)", default=0, type=int, show_default=False)
        filler, mixed, canon = not click.confirm("Auto-skip fillers (defaults to 'N')", default=False), not click.confirm("Auto-skip mixed filler/canon (defaults to 'N')", default=False), not click.confirm("Auto-skip canon (defaults to 'N')", default=False)
        start += offset
        check = (
            lambda x: raw_episodes[offset + x - 1].content_type in ((['Filler'] if filler else []) + (['Mixed Canon/Filler'] if mixed else []) + (['Anime Canon', 'Manga Canon'] if canon else []))
        )
        
        
    for c, stream_urls in enumerate(anime_associator.raw_fetch_using_check(lambda x: check(x) and x >= start), start):
        ts("Active stream session @ [%02d/%s]" % (c, ('%02d' % (len(raw_episodes) - 1)) if raw_episodes else '?'))
        playing = True
        while playing:
            title = "Episode %02d" % c
            if raw_episodes:
                title += ": %s" % raw_episodes[c - 1].title
            
            if not stream_urls:
                ts("Could not find any streams for %s." % title)
                playing = False
                continue
            
            selection = quality_prompt(stream_urls, provider) if len(stream_urls) > 1 else stream_urls.pop()
            headers = selection.get('headers', {})
            _ = headers.pop('ssl_verification', True)
            mpv_process = subprocess.Popen(['mpv', selection.get('stream_url'), "--title=%s" % title] + (['--http-header-fields=%s' % ','.join('%s:%s' % (k, v) for k, v in headers.items())] if headers else []))
            mpv_process.wait()
            
            playing = False
            
            if mpv_process.returncode:
                ts("Detected a non-zero return code.")
                tx("If there was an error or a crash during playback. Don't sweat it, you're going to be prompted for this instance.")
                playing = not click.confirm("Would you like to repeat '%s'? " % title)