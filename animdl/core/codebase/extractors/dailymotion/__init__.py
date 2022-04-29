import functools

import regex

DAILYMOTION_VIDEO = regex.compile(r"/embed/video/([^&?/]+)")
HLS_STREAM_REGEX = regex.compile(r'NAME="(\d+?)",PROGRESSIVE-URI="(.+?)"')


def get_mp4s(session, m3u8_playlist):
    for match in HLS_STREAM_REGEX.finditer(
        session.get(
            m3u8_playlist, headers={"Referer": "https://www.dailymotion.com/"}
        ).text
    ):
        yield {
            "quality": int(match.group(1)),
            "stream_url": match.group(2),
        }


def extract(session, url, **opts):
    match = DAILYMOTION_VIDEO.search(url)

    if not match:
        return []

    metadata_uri = "https://www.dailymotion.com/player/metadata/video/{}".format(
        match.group(1)
    )

    metadata = session.get(metadata_uri).json()

    subtitles = functools.reduce(
        list.__add__,
        (list(data.values()) for _, data in metadata.get("subtitles", {}).get("data")),
        [],
    )

    def genexp():

        for _, streams in metadata.get("qualities", {}).items():
            for stream in streams:
                yield from (
                    list(get_mp4s(session, stream.get("url")))
                    or [{"stream_url": stream.get("url")}]
                )

    return [
        {
            **stream,
            **({"subtitles": subtitles} if subtitles else {}),
        }
        for stream in genexp()
    ]
