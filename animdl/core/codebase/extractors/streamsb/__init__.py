import lxml.html as htmlparser
import regex

DOWNLOAD_CONTENT = regex.compile(r"download_video\('(.+?)','(.+?)','(.+?)'\)")
QUALITY_RE = regex.compile(r"\d+x(\d+)")

def extract(session, url, **opts):
    content = htmlparser.fromstring(session.get(url).text)

    def fast_yield():
        genexp = iter(content.cssselect('tr > td'))
        for link_column, quality_column in zip(genexp, genexp):
            
            links = link_column.cssselect('a')

            if not links:
                continue
            
            quality_match = QUALITY_RE.search(quality_column.text_content())
            quality = int(quality_match.group(1)) if quality_match else None

            content_id, mode, content_hash = DOWNLOAD_CONTENT.search(links[0].get('onclick')).groups()

            download_link = False
            while not download_link:
                download_page = htmlparser.fromstring(session.get('https://sbplay1.com/dl', params={'op': 'download_orig', 'id': content_id, 'mode': mode, 'hash': content_hash}, headers={'referer': url}).text).cssselect('a[href$="mp4"]')

                for direct_download in download_page:
                    yield {'stream_url': direct_download.get('href'), 'headers': {'referer': url}, 'quality': quality}
                    download_link = True
    
    return list(fast_yield())
