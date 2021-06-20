"""
Currently, only GGA streams are supported.
"""

from functools import partial
import lxml.html as htmlparser

import json
import re

ajax_parse = lambda dt: (
    dt.get('source', [{}])[0].get('file'), dt.get('source', [{}])[0].get('label'), dt.get('source', [{}])[0].get('type'), 
    dt.get('source_bk', [{}])[0].get('file'), dt.get('source_bk', [{}])[0].get('label'), dt.get('source_bk', [{}])[0].get('type'))

def fetching_chain(f1, f2, session, url, check=lambda *args: True):
    return f2(session, f1(session, url), check=check)

def from_site_url(session, url) -> dict:
    """
    Keep in mind that the return of this function will vary from stream to stream. (Gogo Anime streams and 4Anime streams will vary.)
    """
    return json.loads(htmlparser.fromstring(session.get(url).content).xpath('//div[@id="epslistplace"]')[0].text)

def bypass_encrypted_content(session, streaming_url):
    with session.get('https:%s' % streaming_url.replace('streaming', 'loadserver')) as server_load:
        for urls in re.finditer(r"(?<=sources:\[{file: ')[^']+", server_load.text):
            yield urls.group(0)

def get_stream_url(session, data_url):
    with session.get('https:%s' % data_url.replace('streaming', 'ajax')) as response:
        content = response.json()
    
    if content == 404:
        return [{'quality': 'unknown', 'stream_url': c, 'headers': {'referer': "https:%s" % data_url}} for c in bypass_encrypted_content(session, data_url)]
        
    s1, l1, t1, s2, l2, t2 =  ajax_parse(content)
    return [{'quality': "%s [%s]" % (l1, t1), 'stream_url': s1}] + ([{'quality': "%s [%s]" % (l2, t2), 'stream_url': s2}] if s2 else [])

def gogoanime_parser(session, data: dict, *, check=lambda *args: True):
    for value in range(data.get('eptotal')):
        if check(value + 1):
            yield partial(lambda s, data_url: get_stream_url(s, data_url), session, data[str(value)]), value + 1