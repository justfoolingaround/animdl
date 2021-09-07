import logging
import os
import time

import httpx
from tqdm import tqdm

from ...config import AUTO_RETRY, QUALITY
from .hls_download import hls_yield


def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f)


def single_threaded_download(url, _path, tqdm_bar_init, headers):
    logger = logging.getLogger("Download @ ".format(_path.stem))

    session = httpx.Client()
    verify = headers.pop('ssl_verification', True)
    response_headers = session.head(
        url,
        allow_redirects=True,
        headers=headers)
    content_length = int(response_headers.headers.get('content-length') or 0)
    tqdm_bar = tqdm_bar_init(content_length)

    with open(_path, 'ab') as sw:
        d = sw.tell()
        tqdm_bar.update(d)
        while content_length > d:
            try:
                with session.stream('GET', url, allow_redirects=True, headers={'Range': 'bytes=%d-' % d, **(headers or {})}, timeout=3) as content_stream:
                    for chunks in content_stream.iter_bytes():
                        size = len(chunks)
                        d += size
                        tqdm_bar.update(size)
                        sw.write(chunks)
            except httpx.HTTPError as e:
                """
                A delay to avoid rate-limit(s).
                """
                logger.error(
                    'Downloading error due to "{!r}", retrying.'.format(e))
                time.sleep(AUTO_RETRY)
    tqdm_bar.close()


def hls_download(
        quality_dict,
        _path,
        episode_identifier,
        _tqdm=True,
        preferred_quality=QUALITY,
        *,
        index_holder,
):

    session = httpx.Client()
    _tqdm_bar = None

    continuator = 1
    if index_holder.exists():
        with open(index_holder, 'r') as ih:
            continuator = int(ih.read() or 1)

    with open(_path, 'ab') as sw, open(index_holder, 'w') as ih_w:
        for content in hls_yield(
                session,
                quality_dict,
                preferred_quality=preferred_quality,
                auto_retry=AUTO_RETRY,
                continuation_index=continuator
        ):
            if _tqdm and not _tqdm_bar:
                _tqdm_bar = tqdm(
                    desc="[HLS] %s " %
                    episode_identifier,
                    total=content.get(
                        'total',
                        0),
                    unit='ts',
                    initial=continuator - 1)
            sw.write(content.get('bytes'))
            if _tqdm:
                _tqdm_bar.update(1)
            with open(index_holder, 'w') as ih_w:
                ih_w.write(str(content.get('current', 0) + 1))

    if isinstance(_tqdm_bar, tqdm):
        _tqdm_bar.close()

    os.remove(index_holder)
