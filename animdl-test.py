"""
An effective benchmark on the providers.

Tries to get a single stream link across each provider.
"""

import requests
from core import Associator

def get_animepahe_onepiece():
    """
    AnimePahe seems to randomize their Anime sessions.
    """
    return "https://animepahe.com/anime/%s" % requests.get('https://animepahe.com/api', params={'m': 'search', 'q': 'one piece'}).json().get('data', [{}])[0].get('session')

SITE_BASED = {
    '4Anime': 'https://4anime.to/anime/one-piece',
    '9Anime': 'https://9anime.to/watch/one-piece.ov8',
    'AnimeFreak': 'https://www.animefreak.tv/watch/one-piece',
    'AnimePahe': get_animepahe_onepiece(),
    'Animixplay': 'https://animixplay.to/v1/one-piece',
    'GogoAnime': 'https://www1.gogoanime.ai/category/one-piece',
    'Twist': 'https://twist.moe/a/one-piece',
}

for anime, anime_url in SITE_BASED.items():
    try:
        episode = [*Associator(anime_url).fetch_appropriate(start=1, end=1)].pop(0)        
        print("Fetch from \x1b[34m{}\x1b[39m has been deemed \x1b[32msuccessful\x1b[39m: {}".format(anime, episode.urls))
    except Exception as e:
        print("Fetch from \x1b[34m{}\x1b[39m has \x1b[31mfailed\x1b[39m, cause of failure: {}".format(anime, e))