import click
import requests

from ... import Associator
from ..helpers import *

@click.command(name='grab', help="Stream the stream links to the stdout stream for external usage.")
@click.option('-q', '--query', help="A search query or anime url string to begin scraping from.", required=True)
@click.option('-s', '--start', help="An integer that determines where to begin the streaming from.", required=False, default=1, show_default=False, type=int)
def animdl_grab(query, start):    
    session = requests.Session()
    anime, provider = process_query(session, query)
    ts = lambda x: to_stdout(x, 'animdl-%s-grabber-core' % provider)
    anime_associator = Associator(anime.get('anime_url'))
    ts("Initializing grabbing session.")    
    for stream_url_caller, episode in anime_associator.raw_fetch_using_check(check=lambda x: x >= start):
        stream_url = stream_url_caller()
        to_stdout(stream_url, 'E%02d' % episode)
    ts("Grabbing session complete.")