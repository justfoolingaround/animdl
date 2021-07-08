import click
import requests

from ...codebase import Associator
from ..helpers import *

import json

@click.command(name='grab', help="Stream the stream links to the stdout stream for external usage.")
@click.argument('query', required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the grabbing from.", required=False, default=1, show_default=False, type=int)
@click.option('-e', '--end', help="A integer that determines where to end the grabbing at.", required=False, default=0, show_default=False, type=int)
@click.option('-f', '--file', help="File to write all the grabbed content to.", required=False, default='', show_default=False, type=str)
@click.option('--auto', is_flag=True, default=False, help="Select the first given index without asking for prompts.")
@click.option('-i', '--index', required=False, default=0, show_default=False, type=int, help="Index for the auto flag.")
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@bannerify
def animdl_grab(query, start, end, file, auto, index, quiet):
    end = end or float('inf')
    session = requests.Session()
    anime, provider = process_query(session, query, auto=auto, auto_index=index)
    if not anime:
        return
    ts = lambda x: to_stdout(x, 'animdl-%s-grabber-core' % provider) if not quiet else None
    anime_associator = Associator(anime.get('anime_url'))
    ts("Initializing grabbing session.")
    collected_streams = []

    if file:
        file += ".json" if not file.endswith('.json') else ''

    for stream_url_caller, episode in anime_associator.raw_fetch_using_check(check=lambda x: end >= x >= start):
        stream_url = stream_url_caller()
        collected_streams.append({'episode': episode, 'streams': stream_url})
        if file:
            to_stdout('Write -> "%s"' % file, 'E%02d' % episode)
            try:
                with open(file, 'w') as json_file_writer:
                    json.dump(collected_streams, json_file_writer, indent=4)
            except WindowsError:
                ts("Failed to attempt I/O on the file at the moment; the unwritten values will be written in the next I/O.")
        else:
            to_stdout(json.dumps({'episode': episode, 'streams': stream_url}), ('E%02d' % episode) if not quiet else '')
    ts("Grabbing session complete.")