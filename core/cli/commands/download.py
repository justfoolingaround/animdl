import os
from pathlib import Path

import click
import requests
from tqdm import tqdm

from ...codebase import (Associator, aed, get_filler_list, hls_download,
                         sanitize_filename, url_download)
from ...config import QUALITY, SESSION_FILE
from ..helpers import *


@click.command(name='download', help="Download your favorite anime by query.")
@click.argument('query', required=True)
@click.option('-a', '--anonymous', is_flag=True, default=False, help='Avoid writing session files for this session.')
@click.option('-s', '--start', help="An integer that determines where to begin the downloading from.", required=False, default=0, show_default=False, type=int)
@click.option('-e', '--end', help="A integer that determines where to end the downloading at.", required=False, default=0, show_default=False, type=int)
@click.option('-q', '--quality', help='Select a preferred quality if available.', required=False, default=QUALITY, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL. This will be used as the download folder name.", required=False, default='', show_default=False)
@click.option('-fl', '--filler-list', help="Filler list associated with the content enqueued for the download.", required=False, default='', show_default=False)
@click.option('-o', '--offset', help="Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 26).", required=False, default=0, show_default=False)
@click.option('--filler', is_flag=True, default=True, help="Auto-skip fillers (If filler list is configured).")
@click.option('--mixed', is_flag=True, default=True, help="Auto-skip mixed fillers/canons (If filler list is configured).")
@click.option('--canon', is_flag=True, default=True, help="Auto-skip canons (If filler list is configured).")
@click.option('--idm', is_flag=True, default=False, help="Download anime using Internet Download Manager")
@click.option('--auto', is_flag=True, default=False, help="Select the first given index without asking for prompts.")
@click.option('-i', '--index', required=False, default=0, show_default=False, type=int, help="Index for the auto flag.")
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@bannerify
def animdl_download(query, anonymous, start, end, quality, title, filler_list, offset, filler, mixed, canon, idm, auto, index, quiet):
    """
    Download call.
    """
    end = end or float('inf')
    
    session = requests.Session()
    
    anime, provider = process_query(session, query, auto=auto, auto_index=index)
    if not anime:
        return
    ts = lambda x: to_stdout(x, 'animdl-%s-downloader-core' % provider) if not quiet else None
    content_name = title or anime.get('name')
    if not content_name:
        content_name = choice(create_random_titles())
        ts("Could not get the folder to download to, generating a cool random folder name: %s" % content_name)
    ts("Initializing download session [%02d -> %s]" % (start, '%02d' % end if isinstance(end, int) else '?'))    
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
    
    if not anonymous:
        sessions.save_session(SESSION_FILE, url, start, content_name, filler_list, offset, filler, mixed, canon, t='download', end=end)
    
    base = Path('./%s/' % sanitize_filename(content_name.strip()))
    base.mkdir(exist_ok=True)
    
    streams = [*anime_associator.raw_fetch_using_check(lambda x: check(x) and end >= x >= start)]
    end_str = '%02d' % end if isinstance(end, int) else (start + len(streams) - 1) if not raw_episodes else len(raw_episodes)
    ts("Starting download session [%02d -> %s]" % (start, end_str))
    ts("Downloads will be done in the folder '%s'" % content_name)
    
    for stream_url_caller, c in streams:
        stream_urls = stream_url_caller()
        
        if not anonymous:
            sessions.save_session(SESSION_FILE, url, c, content_name, filler_list, offset, filler, mixed, canon, t='download', end=end, idm=idm)
        
        content_title = "E%02d" % c
        if raw_episodes:
            content_title += " - %s" % raw_episodes[c - 1].title.strip()
                
        if not stream_urls:
            ts("Failed to download '%s' due to lack of stream urls." % content_title)
            continue
        
        available_qualities = [*filter_quality(stream_urls, quality)]
        if not available_qualities:
            content = stream_urls[0]
            q = content.get('quality')
            if q not in ['multi']:
                ts("Can't find the quality '{}' for {!r}; falling back to {}.".format(quality, content_title, q if q != 'unknown' else 'an unknown quality'))
        else:
            content = available_qualities.pop(0)

        q = content.get('quality')

        if q not in ['unknown', 'multi'] and int(q or 0) != quality:
            ts("Fell back to quality '{}' due to unavailability of '{}'.".format(q, quality))

        extension = aed(content.get('stream_url'))
        if extension in ['php', 'html']:
            extension = 'mp4'
        file_path = Path('%s.%s' % (sanitize_filename(content_title), extension or 'mp4'))
        download_path = base / file_path
                
        if extension in ['m3u', 'm3u8']:
            hls_download(stream_urls, base / ("%s.ts" % sanitize_filename(content_title)), content_title, preferred_quality=quality)
            continue
        
        if idm:
            from ...codebase.downloader import idmanlib
            if idmanlib.supported():
                if download_path.exists():
                    download_path.chmod(0x1ff)
                    os.remove(download_path.as_posix())
                ts("Downloading with Internet Download Manager [%02d/%s]" % (c, end_str))
                idmanlib.wait_until_download(content.get('stream_url'), headers=content.get('headers', {}), filename=file_path, download_folder=base.absolute())
                continue
        
        url_download(content.get('stream_url'), download_path, lambda r: tqdm(desc=content_title, total=r, unit='B', unit_scale=True, unit_divisor=1024), content.get('headers', {}))