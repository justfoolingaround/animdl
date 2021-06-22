from .....config import NINEANIME

import re


VIDSTREAM_REGEXES = {
    'online': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?vidstreamz\.online/(?:e|embed)/(?P<id>[A-Z0-9]+)"),
        'info_ajax': 'https://vidstreamz.online/info/%s',
        },
    'pro': {
        'matcher': re.compile(r"(?:https?://)?(?:\S+\.)?vidstream\.pro/(?:e|embed)/(?P<id>[A-Z0-9]+)"),
        'info_ajax': 'https://vidstream.pro/info/%s',
        },
}
SKEY_RE = re.compile(r"skey = '(?P<skey>[^']+)';")


def uri_correction(vidstream_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    for content, data in VIDSTREAM_REGEXES.items():
            match = data.get('matcher').search(vidstream_uri)
            if match:
                return data.get('info_ajax', '') % match.group('id'), "https://vidstream.pro/e/%s" % match.group('id')
        
def extract(session, vidstream_uri):
    """
    A safe extraction for VidStream.
    """
    info_ajax, vidstream_uri = uri_correction(vidstream_uri)
    
    with session.get(vidstream_uri, headers={'referer': NINEANIME}) as vidstream_content:
        skey_match = SKEY_RE.search(vidstream_content.text)    
        if not skey_match:
            if vidstream_content.ok:
                print('[\x1b[31manimdl-warning\x1b[39m] Could not find session key from VidStream; associated url: "%s" (Include this in your GitHub issue!).' % vidstream_uri)
            return []
            
    with session.get(info_ajax, params={'skey': skey_match.group('skey')}, headers={'referer': vidstream_uri}) as vidstream_info:
        return [{'quality': content.get('label', 'unknown'), 'stream_url': content.get('file', ''), 'headers': {'referer': vidstream_uri}} for content in vidstream_info.json().get('media', {}).get('sources', [])] 
    