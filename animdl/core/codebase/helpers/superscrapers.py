import yarl

from animdl.utils.optopt import regexlib

VRV_RESPONSE_REGEX = regexlib.compile(
    r"^#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(?P<resolution>\d+).*?\n(.+?)$",
    flags=regexlib.MULTILINE,
)
WIXMP_URL_REGEX = regexlib.compile(
    r"https://.+?/(?P<base>.+?/),(?P<resolutions>(?:\d+p,)+)"
)


def iter_ufph_vrv(session, url: yarl.URL, *, stream_attribs=None):

    if stream_attribs is not None:
        vrv_preferences = stream_attribs.pop("vrv", None)

        if vrv_preferences is not None:
            stream_language = vrv_preferences["stream_type"][9:] or None

            if (
                stream_language
                != vrv_preferences["provider_configuration"]["subtitle_language"]
            ):
                return

    hls_response = session.get(url.human_repr()).text

    for match in VRV_RESPONSE_REGEX.finditer(hls_response):
        stream_url = match.group(2).replace("/index-v1-a1.m3u8", "")

        yield {
            "stream_url": stream_url,
            "quality": int(match.group(1)),
            **(stream_attribs or {}),
        }


def iter_ufph_wixmp(session, url: yarl.URL, *, stream_attribs=None):

    match = WIXMP_URL_REGEX.search(url.human_repr())

    if match is None:
        return

    base_url = match.group("base")

    for resolution in match.group("resolutions").split(",")[:-1]:

        stream_url = f"https://{base_url}{resolution}/mp4/file.mp4"

        yield {
            "stream_url": stream_url,
            "quality": int(resolution[:-1]),
            **(stream_attribs or {}),
        }


UNPACKER_MAPPING = {
    "v.vrv.co": iter_ufph_vrv,
    "repackager.wixmp.com": iter_ufph_wixmp,
}


def iter_unpacked_from_packed_hls(session, url: yarl.URL, *, stream_attribs=None):

    host = url.host

    generator = UNPACKER_MAPPING.get(host, None)

    if generator is None:
        yield {
            "stream_url": url.human_repr(),
            **(stream_attribs or {}),
        }
    else:
        yield from generator(session, url, stream_attribs=stream_attribs)
