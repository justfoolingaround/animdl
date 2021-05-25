import subprocess

import click
import requests
from pathlib import Path
from tqdm import tqdm

from ... import Associator
from ...animefillerlist import get_filler_list
from ...downloader import *
from ..helpers import *

@click.command(name='download')
@click.option('-q', '--query', required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the downloading from.", required=False, default=0, show_default=False, type=int)
@click.option('-e', '--end', help="A integer that determines where to end the downloading at.", required=False, default=0, show_default=False, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL. This will be used as the download folder name.", required=False, default='', show_default=False)
def animdl_download(query, start, end, title):
    """
    Download call.
    """
    end = end or float('inf')
    
    session = requests.Session()
    
    anime, provider = process_query(session, query)
    ts = lambda x: to_stdout(x, 'animdl-%s-downloader-core' % provider)
    tx = lambda x: to_stdout(x, 'animdl-protip')
    content_name = title or anime.get('name')
    if not content_name:
        content_name = create_random_titles()[0]
        ts("Could not get the folder to download to, generating a cool random folder name: %s" % content_name)    
    
    if not start:
        start = click.prompt("Episode number to intiate downloading from (defaults to 1)", default=1, show_default=False) or 1
    
    ts("Initialzing download session @ [%02d/%s]" % (start, '%02d' % end if not isinstance(end, float) else '?'))    
    anime_associator = Associator(anime.get('anime_url'))    
    check = lambda *args, **kwargs: True
    raw_episodes = []
    
    tx("Load AnimeFillerList for scraping out episodes?")
    tx("AnimeFillerList allows you to get episode names, filter out filler content & aware the streamer about the index of last episode.")
    tx("A few seconds of configuring could provide all your downloads with a good title.")
    
    if click.confirm("Configure AnimeFillerList settings? (defaults to 'N')", default=False):
        tx("Now configuring AnimeFillerList; please read the stdout stream below to be aware about what to enter.")
        tx("Required: AnimeFillerList URL.")
        tx("Optional: Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 27)")
        tx("Optional: Auto-skip fillers content.")
        tx("Optional: Auto-skip mixed filler/canon content.")
        tx("Optional: Auto-skip canon content.")
        afl_url = click.prompt("Filler list URL")
        raw_episodes = get_filler_list(session, afl_url, fillers=True)
        tx("Succesfully loaded the filler list from '%s'." % afl_url)
        offset = click.prompt("Content offset", default=0, type=int, show_default=False)
        filler, mixed, canon = not click.confirm("Auto-skip fillers (defaults to 'N')", default=False), not click.confirm("Auto-skip mixed filler/canon (defaults to 'N')", default=False), not click.confirm("Auto-skip canon (defaults to 'N')", default=False)
        start += offset
        check = (
            lambda x: raw_episodes[offset + x - 1].content_type in ((['Filler'] if filler else []) + (['Mixed Canon/Filler'] if mixed else []) + (['Anime Canon', 'Manga Canon'] if canon else []))
        )
    
    ts("Starting download session @ [%02d/%s]" % (start, ('%02d' % end if isinstance(end, int) else '?')))
    ts("Downloads will be done in the folder '%s'" % content_name)
    
    base = Path('./%s/' % sanitize_filename(content_name))
    base.mkdir(exist_ok=True)
    
    for c, stream_urls in enumerate(anime_associator.raw_fetch_using_check(lambda x: check(x) and end >= x >= start), start):
        content_title = "E%02d" % c
        if raw_episodes:
            content_title += " - %s" % raw_episodes[c - 1].title
        
        valid_urls = [_ for _ in stream_urls if not aed(_.get('stream_url', '')) in ['m3u8', 'm3u8']]
        
        if not valid_urls:
            ts("Failed to download '%s' due to lack of downloadable stream urls. (Possible that m3u8 streams were only available in the site.)" % content_title)
        
        content = valid_urls[0]
        url_download(content.get('stream_url'), base / Path('%s.%s' % (content_title, aed(content.get('stream_url')))), lambda r: tqdm(desc=content_title, total=r, unit='B', unit_scale=True, unit_divisor=1024), content.get('headers', {}))