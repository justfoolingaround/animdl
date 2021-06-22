from .....config import NINEANIME

import re

SKEY_RE = re.compile(r"skey = '(?P<skey>[^']+)';")


def uri_correction(mcloud_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    content_id = re.search(r"embed/(\w+)", mcloud_uri).group(1)
    return "https://mcloud.to/info/%s" % content_id, "https://mcloud.to/embed/%s" % content_id
    
def extract(session, mcloud_uri):
    """
    A safe extraction for MyCloud.
    """
    info_ajax, mcloud_uri = uri_correction(mcloud_uri)
    
    with session.get(mcloud_uri, headers={'referer': NINEANIME}) as mcloud_content:
        skey_match = SKEY_RE.search(mcloud_content.text)    
        if not skey_match:
            if mcloud_content.ok:
                print('[\x1b[31manimdl-warning\x1b[39m] Could not find session key from MyCloud; associated url: "%s" (Include this in your GitHub issue!).' % mcloud_uri)
            return []
            
    with session.get(info_ajax, params={'skey': skey_match.group('skey')}, headers={'referer': mcloud_uri}) as mcloud_info:
        return [{'quality': content.get('label', 'unknown'), 'stream_url': content.get('file', ''), 'headers': {'referer': mcloud_uri}} for content in mcloud_info.json().get('media', {}).get('sources', [])] 
    