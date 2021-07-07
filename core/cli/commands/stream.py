import click
import requests

from ...codebase import Associator, get_filler_list
from ...config import SESSION_FILE, DEFAULT_PLAYER
from ..helpers import *


def quality_prompt(stream_list, provider):
    ts = lambda x: to_stdout(x, "animdl-%s-url-selector" % provider)
    ts("Found %d stream(s)" % len(stream_list))
    for n, anime in enumerate(stream_list, 1):
        q = anime.get('quality')
        ts("[#%02d]%s %s " % (n, (" [Q.:%s]" % q) if q and not q == 'unknown' else '', stream_judiciary(anime.get('stream_url'))))
    
    index = click.prompt("[\x1b[33m%s\x1b[39m] Select by the index (defaults to 1)" % ('animdl-%s-streamer-core' % provider), default=1, type=int, show_default=False) - 1
    
    if (index + 1) > len(stream_list):
        ts("Applying modulus to get a valid index from incorrect index: #%02d -> #%02d" % (index + 1, index % len(stream_list) + 1))
        index %= len(stream_list)
    
    return stream_list[index]

@click.command(name='stream', help="Stream your favorite anime by query.")
@click.argument('query', required=True)
@click.option('-a', '--anonymous', is_flag=True, default=False, help='Avoid writing session files for this session.')
@click.option('-s', '--start', help="An integer that determines where to begin the streaming from.", required=False, default=0, show_default=False, type=int)
@click.option('-t', '--title', help="Optional title for the anime if the query is a direct URL.", required=False, default='', show_default=False)
@click.option('-fl', '--filler-list', help="Filler list associated with the content enqueued for the stream.", required=False, default='', show_default=False)
@click.option('-o', '--offset', help="Offset (If the E1 of your anime is marked as E27 on AnimeFillerList, this value should be 26s).", required=False, default=0, show_default=False)
@click.option('--player-opts', help='Arguments that are to be passed to the player call.', required=False)
@click.option('--mpv', is_flag=True, default=DEFAULT_PLAYER == 'mpv', flag_value=True, help="Force mpv (defaults to True) for streaming.")
@click.option('--vlc', is_flag=True, default=DEFAULT_PLAYER == 'vlc', flag_value=True, help="Force vlc for streaming.")
@click.option('--filler', is_flag=True, default=True, help="Auto-skip fillers (If filler list is configured).")
@click.option('--mixed', is_flag=True, default=True, help="Auto-skip mixed fillers/canons (If filler list is configured).")
@click.option('--canon', is_flag=True, default=True, help="Auto-skip canons (If filler list is configured).")
@click.option('--auto', is_flag=True, default=False, help="Select the first given index without asking for prompts.")
@click.option('-i', '--index', required=False, default=0, show_default=False, type=int, help="Index for the auto flag.")
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@bannerify
def animdl_stream(query, anonymous, start, title, filler_list, offset, 
                  player_opts, mpv, vlc, filler, mixed, canon, auto, index, quiet):
    """
    Streamer call for animdl streaming session.
    """    
    session = requests.Session()
    
    streamer = handle_streamer(click.parser.split_arg_string(player_opts or '') or [], vlc=vlc, mpv=mpv)
    if streamer == -107977:
        return to_stdout('Streaming failed due to selection of a unsupported streamer; please configure the streamer in the config to use it.', caller='animdl-stream-failure')
    
    anime, provider = process_query(session, query, auto=auto, auto_index=index)
    ts = lambda x: to_stdout(x, 'animdl-%s-streamer-core' % provider) if not quiet else None
    ts('Now initiating your stream session')
    content_name = title or anime.get('name') or choice(create_random_titles())
    ts("Starting stream session @ [%02d/?]" % start)
    url = anime.get('anime_url')
    anime_associator = Associator(url, session=session)    
    check = lambda *args, **kwargs: True
    raw_episodes = []
    
    if filler_list:
        raw_episodes = get_filler_list(session, filler_list, fillers=True)
        ts("Succesfully loaded the filler list from '%s'." % filler_list)
        start += offset
        check = (lambda x: raw_episodes[offset + x - 1].content_type in ((['Filler'] if filler else []) + (['Mixed Canon/Filler'] if mixed else []) + (['Anime Canon', 'Manga Canon'] if canon else [])))
    
    if not anonymous:
        sessions.save_session(SESSION_FILE, url, start, content_name, filler_list, offset, filler, mixed, canon)
    
    streams = [*anime_associator.raw_fetch_using_check(lambda x: check(x) and x >= (start if start >= 0 else 0))]
    if start < 0:
        start += len(streams) + 1
        streams = [(_, __) for _, __ in streams if __ >= start]

    for stream_urls_caller, c in streams:
        if not anonymous:
            sessions.save_session(SESSION_FILE, url, c, content_name, filler_list, offset, filler, mixed, canon)
        playing = True
        while playing:
            title = "Episode %02d" % c
            if raw_episodes:
                title += ": %s" % raw_episodes[c - 1].title
            
            stream_urls = stream_urls_caller()
            
            if not stream_urls:
                playing = not click.confirm("[\x1b[33m%s\x1b[39m] Could not find any streams for %s; continue? " % ('animdl-%s-streamer-core' % provider, title))
                continue
            
            selection = quality_prompt(stream_urls, provider) if len(stream_urls) > 1 else stream_urls[0]
            headers = selection.get('headers', {})
            _ = headers.pop('ssl_verification', True)
            ts("Active stream session @ [%02d/%02d]" % (c, (start + len(streams) - 1) if not raw_episodes else len(raw_episodes)))
            
            player_process = streamer(selection.get('stream_url'), headers=headers, content_title=title)
            player_process.wait()
            playing = False
            
            if player_process.returncode:
                ts("Detected a non-zero return code. [%d]" % player_process.returncode)
                ts("If there was an error or a crash during playback. Don't sweat it, you're going to be prompted for this instance.")
                playing = click.confirm("[\x1b[33m%s\x1b[39m] Would you like to repeat '%s'? " % ('animdl-%s-streamer-core' % provider, title))
