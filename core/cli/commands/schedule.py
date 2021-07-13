from datetime import datetime

import click
import requests

from ...config import ANICHART, DATE_FORMAT, TIME_FORMAT
from ..helpers import bannerify

gql = "query (\n\t$weekStart: Int,\n\t$weekEnd: Int,\n\t$page: Int,\n){\n\tPage(page: $page) {\n\t\tpageInfo {\n\t\t\thasNextPage\n\t\t\ttotal\n\t\t}\n\t\tairingSchedules(\n\t\t\tairingAt_greater: $weekStart\n\t\t\tairingAt_lesser: $weekEnd\n\t\t) {\n\t\t\tid\n\t\t\tepisode\n\t\t\tairingAt\n\t\t\tmedia {\n\t\t\t\t\nid\nidMal\ntitle {\n\tromaji\n\tnative\n\tenglish\n}\nstartDate {\n\tyear\n\tmonth\n\tday\n}\nendDate {\n\tyear\n\tmonth\n\tday\n}\nstatus\nseason\nformat\ngenres\nsynonyms\nduration\npopularity\nepisodes\nsource(version: 2)\ncountryOfOrigin\nhashtag\naverageScore\nsiteUrl\ndescription\nbannerImage\nisAdult\ncoverImage {\n\textraLarge\n\tcolor\n}\ntrailer {\n\tid\n\tsite\n\tthumbnail\n}\nexternalLinks {\n\tsite\n\turl\n}\nrankings {\n\trank\n\ttype\n\tseason\n\tallTime\n}\nstudios(isMain: true) {\n\tnodes {\n\t\tid\n\t\tname\n\t\tsiteUrl\n\t}\n}\nrelations {\n\tedges {\n\t\trelationType(version: 2)\n\t\tnode {\n\t\t\tid\n\t\t\ttitle {\n\t\t\t\tromaji\n\t\t\t\tnative\n\t\t\t\tenglish\n\t\t\t}\n\t\t\tsiteUrl\n\t\t}\n\t}\n}\n\n\n\t\t\t}\n\t\t}\n\t}\n}"

def arrange_template(data):
    content = {}

    for airing in data[::-1]:
        dtobj = datetime.fromtimestamp(airing.get('airingAt', 0))
        d, t = dtobj.strftime(DATE_FORMAT), dtobj.strftime(TIME_FORMAT)
        titles = airing.get('media', {}).get('title', {})
        title = titles.get('english') or titles.get('romanji') or titles.get('native')
        content.setdefault(d, {})
        content[d].setdefault(t, [])
        content[d][t].append({'anime': title, 'episode': airing.get('episode', 0), 'datetime_object': dtobj})

    return content

@click.command(name='schedule', help="Know which animes are going over the air when.")
@click.option('--quiet', help='A flag to silence all the announcements.', is_flag=True, flag_value=True)
@bannerify
def animdl_schedule(quiet):    
    
    has_next_page, page = True, 1
    schedules = []
    session = requests.Session()

    unix_time = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

    while has_next_page:
        with session.post(ANICHART, json={'query': gql, 'variables': {'weekStart': unix_time, 'weekEnd': unix_time + 24*7*60*60, 'page': page}}) as schedule_data:
            data = schedule_data.json()
            schedules.extend(data.get('data', {}).get('Page', {}).get('airingSchedules', []))
            has_next_page = data.get('data', {}).get('Page', {}).get('pageInfo', {}).get('hasNextPage', False)
            page += 1
            

    for date, _content in arrange_template(schedules).items():
        print("On \x1b[33m{}\x1b[39m,".format(date))
        for time, __content in sorted(_content.items(), key=lambda d: d[1][0].get('datetime_object'), reverse=True):
            print("\t\x1b[95m{}\x1b[39m - {}".format(time, ', '.join("{anime} [\x1b[94mE{episode}\x1b[39m]".format_map(___content) for ___content in __content)))
