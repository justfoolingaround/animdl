"""
Currently, only GGA streams are supported.
"""

import requests
import lxml.html as htmlparser

import asyncio
import json
import re

loop = asyncio.get_event_loop()

try:
    from asyncio import to_thread
except ImportError:
    to_thread = lambda f, *args, **kwargs: loop.run_in_executor(None, f, *args, **kwargs)


def from_site_url(url) -> dict:
    """
    Keep in mind that the return of this function will vary from stream to stream. (Gogo Anime streams and 4Anime streams will vary.)
    """
    return json.loads(htmlparser.fromstring(requests.get(url).content).xpath('//div[@id="epslistplace"]')[0].text)

def gogoanime_ajax_parse(data: dict):
    return data.get('source', [{}])[0].get('file'), data.get('source_bk', [{}])[0].get('file')

def gogoanime_parser(data: dict, *, check=lambda *args: True):
    
    for value in range(data.get('eptotal')):
        if check(value):
            yield gogoanime_ajax_parse(json.loads(requests.get("https:%s" % data[str(value)].replace('streaming', 'ajax')).content))
        
def gogoanime_parser_v2(data: dict, *, check=lambda *args: True):
    
    async def parse(url):
        return gogoanime_ajax_parse((await to_thread(requests.get, "https:%s&referer=none" % url.replace('streaming', 'ajax'))).content)
        
    return loop.run_until_complete(asyncio.gather(*[parse(data[str(value)]) for value in range(data.get('eptotal')) if check(value)]))

AVAILABLE_PARSERS = {
    'gogo-anime': {
        'matcher': re.compile(r'^(?:https?:\/\/)animixplay\.to\/v1\/\S+'),
        'parser': gogoanime_parser
    }
}

def get_parser(url):
    
    for parser, data in AVAILABLE_PARSERS.items():
        if data.get('matcher').match(url):
            return data.get('parser')