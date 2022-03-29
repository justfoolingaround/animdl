import logging

import regex
import yarl
from Cryptodome.Cipher import AES

from ...cli.helpers import intelliq

ENCRYPTION_DETECTION_REGEX = regex.compile(r"#EXT-X-KEY:METHOD=([^,]+),")
ENCRYPTION_URL_IV_REGEX = regex.compile(
    r'#EXT-X-KEY:METHOD=(?P<method>[^,]+),URI="(?P<key_uri>.+?)"(?:,IV=(?P<iv>.*))?'
)


STREAM_INFO_REGEX = regex.compile(r"#EXT-X-STREAM-INF(:.*?)?\n+(.+)")
QUALITY_REGEX = regex.compile(r"RESOLUTION=\d+x(\d+)")

INTERNAL_STREAMS_REGEX = regex.compile(r"#EXTINF:.+?\n+(.+)")

HLS_STREAM_EXTENSIONS = ["m3u8", "m3u"]


def get_extension(url):
    _, _, extension = yarl.URL(url).name.rpartition(".")
    return extension


def extract_resolution(quality_string):
    resolution = QUALITY_REGEX.search(quality_string)
    if resolution:
        return resolution.group(1)


def def_iv(initial=1):
    while True:
        yield initial.to_bytes(16, "big")
        initial += 1


def get_decrypter(key, *, iv=b"", default_iv_generator):
    if not iv:
        iv = next(default_iv_generator)
    return AES.new(key, AES.MODE_CBC, iv).decrypt


def unencrypted(m3u8_content):
    st = ENCRYPTION_DETECTION_REGEX.search(m3u8_content)
    return (not bool(st)) or st.group(1) == "NONE"


def extract_encryption(m3u8_content):
    return ENCRYPTION_URL_IV_REGEX.search(m3u8_content).group("key_uri", "iv")


def join_url(parent, child):
    return yarl.URL("{}/{}".format(str(parent).rstrip("/"), str(child).lstrip("/")))


def m3u8_generation(session_init, m3u8_uri):
    m3u8_uri_parent = yarl.URL(m3u8_uri).parent
    response = session_init(m3u8_uri)
    for regex_find in STREAM_INFO_REGEX.finditer(
        response.content.decode("utf-8", errors="ignore")
    ):
        stream_info, content_uri = regex_find.groups()
        url = yarl.URL(content_uri)
        if get_extension(url) in HLS_STREAM_EXTENSIONS:
            if not url.is_absolute():
                content_uri = join_url(m3u8_uri_parent, url)
            yield from m3u8_generation(session_init, content_uri)
        yield {"quality": extract_resolution(stream_info), "stream_url": content_uri}


def resolve_stream(session, logger, q_dicts, quality_string):
    for origin_m3u8 in intelliq.filter_quality(q_dicts, quality_string):
        headers = origin_m3u8.get("headers", {})

        m3u8s = list(
            m3u8_generation(
                lambda s: session.get(str(s), headers=headers),
                origin_m3u8.get("stream_url"),
            )
        )
        for m3u8 in intelliq.filter_quality(m3u8s, quality_string):
            content_response = session.get(str(m3u8.get("stream_url")), headers=headers)
            if content_response.status_code < 400:
                return content_response, origin_m3u8
        content_response = session.get(
            str(origin_m3u8.get("stream_url")), headers=headers
        )
        if content_response.status_code < 400:
            return content_response, origin_m3u8


def hls_yield(session, q_dicts, quality_string, auto_retry=2, *, continuation_index=1):

    logger = logging.getLogger("hls/internal")

    content_response, origin_m3u8 = resolve_stream(
        session, logger, q_dicts, quality_string
    )

    m3u8_data = content_response.content.decode("utf-8", errors="ignore")

    base_uri = yarl.URL(str(content_response.url).rstrip("/") + "/").parent
    encryption_uri, encryption_iv, encryption_data = None, None, b""
    encryption_state = not unencrypted(m3u8_data)

    if encryption_state:
        encryption_uri, encryption_iv = extract_encryption(m3u8_data)
        parsed_uri = yarl.URL(encryption_uri)
        if not parsed_uri.is_absolute():
            parsed_uri = base_uri.join(parsed_uri)
        encryption_key_response = session.get(
            parsed_uri.human_repr(), headers=origin_m3u8.get("headers", {})
        )
        encryption_data = encryption_key_response.content

    internal_streams = INTERNAL_STREAMS_REGEX.findall(m3u8_data)
    total_streams = len(internal_streams)

    stream_iter = iter(
        (yarl.URL(_) for _ in internal_streams[continuation_index - 1 :])
    )
    if encryption_state:
        decryptor = get_decrypter(
            encryption_data,
            iv=encryption_iv or None,
            default_iv_generator=def_iv(continuation_index),
        )

    for current_count, stream in enumerate(stream_iter, continuation_index):

        if not stream.is_absolute():
            stream = base_uri.join(stream)

        ts_response = session.get(
            stream.human_repr(), headers=origin_m3u8.get("headers", {})
        )

        ts_response.raise_for_status()
        ts_data = ts_response.content

        if encryption_state:
            ts_data = decryptor(ts_data)

        yield {
            "bytes": ts_data,
            "total": total_streams,
            "current": current_count,
        }
