import click
import requests

from ... import Associator
from ..helpers import *

import json

@click.command(name='grab', help="Stream the stream links to the stdout stream for external usage.")
@click.option('-q', '--query', help="A search query or anime url string to begin scraping from.", required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the grabbing from.", required=False, default=1, show_default=False, type=int)
@click.option('-e', '--end', help="A integer that determines where to end the grabbing at.", required=False, default=0, show_default=False, type=int)
@click.option('-f', '--file', help="File to write all the grabbed content to.", required=False, default='', show_default=False, type=str)
def animdl_grab(query, start, end, file):
    end = end or float('inf')
    session = requests.Session()
    anime, provider = process_query(session, query)
    ts = lambda x: to_stdout(x, 'animdl-%s-grabber-core' % provider)
    anime_associator = Associator(anime.get('anime_url'))
    ts("Initializing grabbing session.")
    collected_streams = []    
    for stream_url_caller, episode in anime_associator.raw_fetch_using_check(check=lambda x: end >= x >= start):
        stream_url = stream_url_caller()
        collected_streams.append({'episode': episode, 'streams': stream_url})
        if file:
            file += ".json" if not file.endswith('.json') else ''
            to_stdout('Write -> "%s"' % file, 'E%02d' % episode)
            with open(file, 'w') as json_file_writer:
                json.dump(collected_streams, json_file_writer, indent=4)     
        else:
            to_stdout(stream_url, 'E%02d' % episode)
    ts("Grabbing session complete.")