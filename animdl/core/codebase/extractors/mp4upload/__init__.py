import logging

import regex

MP4UPLOAD_REGEX = regex.compile(r"player\|(.*)\|videojs")


def extract_480(splitted_values):
    return {
        "stream_url": "{4}://{18}.mp4upload.{1}:{70}/d/{69}/{68}.{67}".format(
            *splitted_values
        )
    }


def extract_any(splitted_values):
    return {
        "stream_url": "{3}://{18}.mp4upload.{0}:{73}/d/{72}/{71}.{70}".format(
            *splitted_values
        )
    }


def extract(session, url, **opts):
    logger = logging.getLogger("mp4upload-extractor")

    mp4upload_embed_page = session.get(url)
    if mp4upload_embed_page.text == "File was deleted":
        return []

    content = MP4UPLOAD_REGEX.search(mp4upload_embed_page.text).group(1).split("|")

    try:
        return [
            {
                **(extract_480 if "480" in content else extract_any)(content),
                "headers": {"referer": url, "ssl_verification": False},
            }
        ]
    except Exception as e:
        return logger.error("'%s' occurred when extracting from '%s'." % (e, url)) or []


extract.disabled = True
