import click
import requests

import lxml.html as htmlparser
from datetime import datetime

from ...config import (
    DATE_FORMAT,
    TIME_FORMAT,
    LIVECHART,
)


def arrange_template(element_obj):
    def merge_dicts(dict1, dict2):
        return {**dict2, **{k: (v if not (k in dict2) else (v + dict2.get(k)) if isinstance(v, list) else merge_dicts(v, dict2.get(k))) for k, v in dict1.items()}}
    
    initial = {}

    for content in sorted(element_obj.xpath('//div[@class="schedule-card"]'), key=lambda c: int(c.xpath('time')[0].get('data-timestamp'))):
        ts = content.xpath('time')[0]
        episode = ts.get('data-label', '0').strip('EP')
        datetime_obj = datetime.fromtimestamp(int(ts.get('data-timestamp', 0)))
        initial = merge_dicts(initial, {datetime_obj.strftime(DATE_FORMAT): {datetime_obj.strftime(TIME_FORMAT): [{'anime': content.get('data-title'), 'episode': episode, 'datetime_object': datetime_obj}]}})

    return initial


@click.command(name='schedule', help="Know which animes are going over the air when.")
def animdl_schedule():    
    
    with requests.get(LIVECHART + 'schedule/tv', allow_redirects=True, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.102 Safari/537.36'}) as livechart_page:
        content = arrange_template(htmlparser.fromstring(livechart_page.text))
    
    for date, _content in content.items():
        print("On \x1b[33m{}\x1b[39m,".format(date))
        for time, __content in _content.items():
            print("\t\x1b[95m{}\x1b[39m - {}".format(time, ', '.join("{anime} [\x1b[94mE{episode}\x1b[39m]".format_map(___content) for ___content in __content)))