import re

MP4UPLOAD_REGEX = re.compile(r"player\|(.*)\|videojs")

def uri_correction(mp4upload_uri):
    """
    Compensation for the inaccuracy with url decode that occurs internally in **animdl**.
    """
    return "https://www.mp4upload.com/embed-%s.html" % re.search(r"embed-(.*)\.html", mp4upload_uri).group(1)

def extract_480(splitted_values):
    return {'quality': splitted_values[50], 'stream_url': "{4}://{18}.{3}.{1}:{70}/d/{69}/{68}.{67}".format(*splitted_values)}

def extract_any(splitted_values):
    return {'quality': splitted_values[53], 'stream_url': "{3}://{18}.{1}.{0}:{73}/d/{72}/{71}.{70}".format(*splitted_values)}    

def extract(session, mp4upload_uri):
    """
    A curated-random extraction for MP4Upload.
    """
    mp4upload_uri = uri_correction(mp4upload_uri)
    with session.get(mp4upload_uri) as mp4upload_embed_page:
        if mp4upload_embed_page.text == 'File was deleted':
            return []
        content = MP4UPLOAD_REGEX.search(mp4upload_embed_page.text).group(1).split('|')

        try:
            return [{**(extract_480 if '480' in content else extract_any)(content), 'headers': {'referer': mp4upload_uri, 'ssl_verification': False}}]
        except Exception as e:
            raise Exception("'%s' occurred when extracting from '%s'." % (e, mp4upload_uri))