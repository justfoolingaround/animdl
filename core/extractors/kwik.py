import re

KWIKPLAYER_JAVASCRIPT_REGEX = re.compile(r"Plyr\|querySelector\|document\|([^\\']+)")

def extract(session, content_uri, headers):
    """
    This method uses curated-random extraction. 
    """
    with session.get(content_uri, headers=headers) as kwik_page:
        match = KWIKPLAYER_JAVASCRIPT_REGEX.search(kwik_page.text)
        if match:
            return [{"quality": "unknown", "stream_url": "{10}://{9}-{8}-{7}.{6}.{5}/{4}/{3}/{2}/{1}.{0}".format(*match.group(1).split('|')), "headers": {'referer': content_uri}}]
        raise Exception("Session fetch failure; please recheck and/or retry fetching anime URLs again. If this problem persists, please make an issue immediately.")