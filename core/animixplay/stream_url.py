"""
Currently, only GGA streams are supported.
"""

import requests
import lxml.html as htmlparser

import json

def from_site_url(url) -> dict:
    """
    Keep in mind that the return of this function will vary from stream to stream. (Gogo Anime streams and 4Anime streams will vary.)
    """
    return json.loads(htmlparser.fromstring(requests.get(url).content).xpath('//div[@id="epslistplace"]')[0].text)

def parse_gga(data: dict, *, check=lambda *args: True):
    
    for value in range(data.get('eptotal')):
        if check(value):
            yield ((src := json.loads(requests.get("https:%s" % data[str(value)].replace('streaming', 'ajax')).content)).get('source', [{}])[0].get('file'), src.get('source_bk', [{}])[0].get('file'))
        
def parse_gga_using_async(data: dict, *, check=lambda *args: True):
    
    import asyncio
    
    async def parse(url):
        return ((src := json.loads((await asyncio.to_thread(requests.get, "https:%s&referer=none" % url.replace('streaming', 'ajax'))).content)).get('source', [{}])[0].get('file'), src.get('source_bk', [{}])[0].get('file'))
    
    loop = asyncio.get_event_loop()
    
    return loop.run_until_complete(asyncio.gather(*[parse(data[str(value)]) for value in range(data.get('eptotal')) if check(value)]))
