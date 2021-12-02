import lxml.html as htmlparser
import regex
import yarl


def get_quality(url_text):
    match = regex.search(r'(\d+)P', url_text)
    if not match:
        return None

    return int(match.group(1))

def extract(session, url, **opts):
    """
    Extract content off of GogoAnime.
    """
    parsed_url = yarl.URL(url)

    if not parsed_url.scheme:
        parsed_url = parsed_url.with_scheme('https')
    
    content_url = parsed_url.with_name('download').with_query(parsed_url.query).human_repr()

    response = session.get(
        content_url,
        headers={
            'referer': url})
    content = htmlparser.fromstring(response.text)

    return [{'quality': get_quality(_url.text_content()), 'stream_url': _url.get('href'), 'headers': {'referer': url}} for _url in content.cssselect('.dowload > a[download]')]
