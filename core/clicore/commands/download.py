from pathlib import Path

import click
import requests
from tqdm import tqdm

from ... import Associator
from ...animefillerlist import get_filler_list
from ...downloader import *
from ..helpers import *
from .constants import SESSION_FILE

@click.command(name='download', help="Download your favorite anime by query.")
@click.option('-q', '--query', required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the downloading from.", required=False, default=0, show_default=False, type=int)
@click.option('-e', '--end', help="A integer that determines where to end the downloading at.", required=False, default=0, show_default=False, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL. This will be used as the download folder name.", required=False, default='', show_default=False)
@click.option('-fl', '--filler-list', help="Filler list associated with the content enqueued for the download.", required=False, default='', show_default=False)
@click.option('-o', '--offset', help="Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 26).", required=False, default=0, show_default=False)
@click.option('--filler', is_flag=True, default=True, help="Auto-skip fillers (If filler list is configured).")
@click.option('--mixed', is_flag=True, default=True, help="Auto-skip mixed fillers/canons (If filler list is configured).")
@click.option('--canon', is_flag=True, default=True, help="Auto-skip canons (If filler list is configured).")
def animdl_download(query, start, end, title, filler_list, offset, filler, mixed, canon):
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
        content_name = choice(create_random_titles())
        ts("Could not get the folder to download to, generating a cool random folder name: %s" % content_name)    
    
    if not start:
        start = click.prompt("Episode number to intiate downloading from (defaults to 1)", default=1, show_default=False) or 1
    
    ts("Initialzing download session @ [%02d/%s]" % (start, '%02d' % end if isinstance(end, int) else '?'))    
    url = anime.get('anime_url')
    anime_associator = Associator(url, session=session)    
    check = lambda *args, **kwargs: True
    raw_episodes = []
    
    if filler_list:
        raw_episodes = get_filler_list(session, filler_list, fillers=True)
        ts("Succesfully loaded the filler list from '%s'." % filler_list)
        start += offset
        if not isinstance(end, int):
            end = len(raw_episodes)
        check = (lambda x: raw_episodes[offset + x - 1].content_type in ((['Filler'] if filler else []) + (['Mixed Canon/Filler'] if mixed else []) + (['Anime Canon', 'Manga Canon'] if canon else [])))
    
    ts("Starting download session @ [%02d/%s]" % (start, ('%02d' % end if isinstance(end, int) else '?')))
    ts("Downloads will be done in the folder '%s'" % content_name)
    
    sfhandler.save_session(SESSION_FILE, url, start, content_name, filler_list, offset, filler, mixed, canon, t='download', end=end)
    
    base = Path('./%s/' % sanitize_filename(content_name))
    base.mkdir(exist_ok=True)
    
    for stream_urls, c in anime_associator.raw_fetch_using_check(lambda x: check(x) and end >= x >= start):
        sfhandler.save_session(SESSION_FILE, url, c, content_name, filler_list, offset, filler, mixed, canon, t='download', end=end)
        content_title = "E%02d" % c
        if raw_episodes:
            content_title += " - %s" % raw_episodes[c - 1].title
        
        valid_urls = [_ for _ in stream_urls if not aed(_.get('stream_url', '')) in ['m3u8', 'm3u']]
        
        if not valid_urls:
            ts("Failed to download '%s' due to lack of downloadable stream urls. (Possible that m3u8 streams were only available in the site.)" % content_title)
            if stream_urls:
                ts("Here are some usable streams: %s" % stream_urls)
            continue
        
        content = valid_urls[0]
        url_download(content.get('stream_url'), base / Path('%s.%s' % (content_title, aed(content.get('stream_url')))), lambda r: tqdm(desc=content_title, total=r, unit='B', unit_scale=True, unit_divisor=1024), content.get('headers', {}))