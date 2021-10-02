import re
import lxml.html as htmlparser

DOWNLOAD_CONTENT = re.compile(r"download_video\('(.+?)','(.+?)','(.+?)'\)")

def extract(session, streamsb_url):
    content = htmlparser.fromstring(session.get(streamsb_url).text)

    for links in content.cssselect('a[onclick^="download_video"]'):
        content_id, mode, content_hash = DOWNLOAD_CONTENT.search(links.get('onclick')).groups()

        download_link = False
        while not download_link:
            download_page = htmlparser.fromstring(session.get('https://sbplay.org/dl', params={'op': 'download_orig', 'id': content_id, 'mode': mode, 'hash': content_hash}, headers={'referer': streamsb_url}).text).cssselect('a[href$="mp4"]')

            for direct_download in download_page:
                yield {'stream_url': direct_download.get('href'), 'headers': {'referer': streamsb_url}}
                download_link = True
