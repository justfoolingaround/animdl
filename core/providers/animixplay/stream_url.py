"""
Currently, only GGA streams are supported.
"""

from functools import partial
import lxml.html as htmlparser

import json
import re

def fetching_chain(f1, f2, session, url, check=lambda *args: True):
    return f2(session, f1(session, url), check=check)

def from_site_url(session, url) -> dict:
    """
    Keep in mind that the return of this function will vary from stream to stream. (Gogo Anime streams and 4Anime streams will vary.)
    """
    return json.loads(htmlparser.fromstring(session.get(url).content).xpath('//div[@id="epslistplace"]')[0].text)

def gogoanime_parser(session, data: dict, *, check=lambda *args: True):
    
    ajax_parse = lambda dt: [{'quality': 'unknown', 'stream_url': dt.get('source', [{}])[0].get('file')}, {'quality': 'unknown', 'stream_url': dt.get('source_bk', [{}])[0].get('file')}]
    for value in range(data.get('eptotal')):
        if check(value + 1):
            yield partial(lambda session, data, value: (ajax_parse(session.get("https:%s" % data[str(value)].replace('streaming', 'ajax')).json())), session, data, value), value + 1