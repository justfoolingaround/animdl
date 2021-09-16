import logging
import os
import pathlib
import time

import httpx
import yarl
from tqdm import tqdm

from .content_mt import mimetypes
from .hls import HLS_STREAM_EXTENSIONS, hls_yield
from .ffmpeg import FFMPEG_EXTENSIONS, ffmpeg_download, has_ffmpeg

EXEMPT_EXTENSIONS = ['mpd']

def sanitize_filename(f):
    return ''.join(' - ' if _ in '<>:"/\\|?*' else _ for _ in f).strip()

def get_extension(url):
    url = yarl.URL(url)
    position = url.name.find('.')
    if position == -1:
        return ''
    return url.name[position + 1:]

def guess_extension(content_type):
    for name, cd, extension in mimetypes:
        if cd == content_type:
            return (extension or '').lstrip('.')

def process_url(session, url, headers={}):
    """
    Get the extension, content size and range downloadability forehand.

    Returns:

    `str`, `int`, `bool`
    """
    response = session.head(url, headers=headers)
    response_headers = response.headers
    return (guess_extension(response_headers.get('content-type') or '') or get_extension(url) or get_extension(response.url)).lower(), int(response_headers.get('content-length') or 0), response_headers.get('accept-ranges') == 'bytes'

def standard_download(session: httpx.Client, url: str, content_dir: pathlib.Path, outfile_name: str, extension: str, content_size: int, headers: dict={}, ranges=True, **opts):
    file = "{}.{}".format(outfile_name, extension)

    logger = logging.getLogger('standard-downloader[{}]'.format(file))
    out_path = content_dir / pathlib.Path(sanitize_filename(file))

    if not ranges:
        logger.critical("Stream does not support ranged downloading; failed downloads cannot be continued.")

    with open(out_path, 'ab') as outstream:
        downloaded = outstream.tell() if not ranges else 0
        progress_bar = tqdm(desc="GET / {}".format(file), total=content_size, disable=opts.get('log_level', 20) > 20, initial=downloaded, unit='B', unit_scale=True, unit_divisor=1024)
        while content_size > downloaded:
            temporary_headers = headers.copy()
            if ranges:
                temporary_headers.update({'Ranges': 'bytes={}-'.format(downloaded)})
            try:
                with session.stream('GET', url, allow_redirects=True, headers=headers) as http_stream:
                    for chunks in http_stream.iter_bytes():
                        size = len(chunks)
                        outstream.write(chunks)
                        progress_bar.update(size)
                        downloaded += size
            except httpx.HTTPError as e:
                if not ranges:
                    downloaded = 0
                    outstream.seek(0)
                    progress_bar.clear()
                else:
                    outstream.flush()
                logger.error("Downloading error due to {!r}, retrying.".format(e))
                time.sleep(opts.get('retry_timeout') or 5.0)
    
    progress_bar.close()

def hls_download(session: httpx.Client, url: str, content_dir: pathlib.Path, outfile_name: str, headers: dict={}, **opts):

    sanitized = sanitize_filename(outfile_name)
    content_path = content_dir / "{}.ts".format(sanitized)
    index_holder = content_dir / "{}.partialts".format(sanitized)
    index = 1

    if index_holder.exists():
        with open(index_holder, 'r') as ih:
            index = int(ih.read() or 1)

    sizes = []
    with open(content_path, 'ab') as tsstream, open(index_holder, 'w+') as istream:
        downloaded = tsstream.tell()
        if downloaded:
            sizes.extend([downloaded / index] * index)
        progress_bar = tqdm(desc="HLS GET / {}.ts".format(outfile_name), unit='B', unit_scale=True, unit_divisor=1024, initial=downloaded, disable=opts.get('log_level', 20) > 20,)

        for content in hls_yield(session, [{'stream_url': url, 'headers': headers}], opts.get('preferred_quality') or 1080, opts.get('retry_timeout') or 5, continuation_index=index):
            stream = content.get('bytes')
            total = content.get('total')
            current = content.get('current')

            size = len(stream)
            sizes.append(size)

            mean = (sum(sizes)/len(sizes))
            stddev = (sum(abs(mean - s)**2 for s in sizes)/len(sizes))**.5

            progress_bar.total = mean * total
            progress_bar.desc = 'HLS GET / {}.ts [± {:.3f} MB]'.format(outfile_name, stddev / (1024**2))
            progress_bar.update(size)

            istream.write(str(current or 0 + 1))
            istream.seek(0)
            istream.flush()

            tsstream.write(stream)
        
    progress_bar.close()
    os.remove(index_holder)

def idm_download(url, headers, content_dir, outfile_name, extension, **opts):
    file = "{}.{}".format(outfile_name, extension)
    from .idmanlib import wait_until_download as idmdl    
    idmdl(url, headers=headers or {}, download_folder=content_dir, filename=file)

def handle_download(session, url, headers, content_dir, outfile_name, idm=False, use_ffmpeg=False, **opts):
    
    extension, content_size, ranges = process_url(session, url, headers)

    if use_ffmpeg and (extension in FFMPEG_EXTENSIONS and has_ffmpeg()):
        return ffmpeg_download(url, headers, outfile_name, content_dir, **opts)

    if extension in EXEMPT_EXTENSIONS:
        raise Exception("Download extension {!r} requires custom downloading which is not supported yet.".format(extension))

    if extension in HLS_STREAM_EXTENSIONS:
        return hls_download(session, url, content_dir, outfile_name, headers or {}, **opts)

    if idm:
        return idm_download(url, headers or {}, content_dir, outfile_name, extension, **opts)

    return standard_download(session, url, content_dir, outfile_name, extension, content_size, headers or {}, ranges, **opts)
