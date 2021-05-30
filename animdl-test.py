"""
An effective benchmark on the providers.

Tries to get a single stream link across each provider.
"""

current_version = "20210530-1"

import requests
from core import Associator

SHOW_FULL_URLS = False
LAST_CURATED_TEST = requests.get("https://raw.githubusercontent.com/justfoolingaround/animdl/master/last-curated-test.json").json()
PROVIDERS = LAST_CURATED_TEST.get('status', {})

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

RESULTS = {}

for anime, anime_url in SITE_BASED.items():
    try:
        episode = [*Associator(anime_url).fetch_appropriate(start=1, end=1)].pop(0)        
        print("Fetch from \x1b[36m{}\x1b[39m has been deemed \x1b[32msuccessful\x1b[39m{}".format(anime, (": %s" % episode.urls) if SHOW_FULL_URLS else ''))
        RESULTS.update({anime: True})
    except Exception as e:
        print("Fetch from \x1b[36m{}\x1b[39m has \x1b[31mfailed\x1b[39m, cause of failure: {}".format(anime, e))
        RESULTS.update({anime: False})
        
print("\x1b[33mComparing the test results to the last curated test by AnimDL's developers.\x1b[39m")

for anime, anime_result in RESULTS.items():
    if anime_result:
        if (anime_result != PROVIDERS.get(anime, False)):
            print("\x1b[36m{}\x1b[39m should not be working but is working now; you can raise an issue for requesting an update on this.".format(anime))
        else:
            print("\x1b[36m{}\x1b[39m's status has matched with the curated test.".format(anime))
    else:
        if (anime_result != PROVIDERS.get(anime, False)):  
            print("\x1b[36m{}\x1b[39m is not working as intended; raise an issue immediately to get this fixed!".format(anime))
        else:
            print("\x1b[36m{}\x1b[39m is not working currently, the developers are aware of this and the issue will get fixed soon.".format(anime))
            
if LAST_CURATED_TEST.get('current_version') != current_version:
    print("\x1b[31m{}\x1b[39m".format('The above results are subject to be severely outdated. Please update the code by performing a git pull or re-downloading the repository.'))