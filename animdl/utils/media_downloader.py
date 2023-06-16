"""
async_downloader.py but one that utilises threads.
"""


import threading
import time
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from io import FileIO
    from typing import Optional

    from tqdm import tqdm


class MultiConnectionDownloader:
    MINIMUM_PART_SIZE = 1024**2
    MAX_RETRIES = 5

    def __init__(
        self,
        session: httpx.Client,
        *args,
        progress_bar: "Optional[tqdm]" = None,
        retry_timeout: "Optional[int]" = None,
        **kwargs,
    ):
        self.session = session
        self.progress_bar = progress_bar
        self.retry_timeout = retry_timeout

        self.args = args
        self.kwargs = kwargs

        self.io_lock = threading.Lock()
        self.active_threads: "dict[str, threading.Thread]" = {}
        self.threads_errors: "dict[str, Exception]" = {}

    def download_section(
        self,
        io: "FileIO",
        start: int,
        end: int,
        progress_bar: "Optional[tqdm]" = None,
        pause_event: "Optional[threading.Event]" = None,
        error_event: "Optional[threading.Event]" = None,
    ):
        kwargs = self.kwargs.copy()

        headers = kwargs.pop("headers") or {}
        content_length = end
        position = start or 0

        is_incomplete = lambda: content_length is None or position < content_length
        is_downloading = lambda: (error_event is None or not error_event.is_set()) and (
            pause_event is None or not pause_event.is_set()
        )

        retry_count = 0

        while is_downloading() and is_incomplete():
            if content_length is None:
                if start is not None:
                    headers["Range"] = f"bytes={position}-"
            else:
                headers["Range"] = f"bytes={position}-{content_length}"

            try:
                with self.session.stream(
                    *self.args, **kwargs, headers=headers
                ) as response:
                    content_length = (
                        int(response.headers.get("Content-Length", 0)) or None
                    )

                    if progress_bar is not None:
                        if content_length > 0:
                            progress_bar.total = content_length

                    for chunk in response.iter_bytes(8192):
                        chunk_size = len(chunk)

                        if self.progress_bar is not None:
                            self.progress_bar.update(chunk_size)

                        if progress_bar is not None:
                            progress_bar.update(chunk_size)

                        self.write_to_file(
                            self.io_lock,
                            io,
                            position,
                            chunk,
                        )
                        position += chunk_size

                        if not is_downloading():
                            break

                    if content_length is None:
                        content_length = position

            except httpx.HTTPError as error:
                if retry_count >= self.MAX_RETRIES:
                    locks = ()

                    if progress_bar is not None:
                        locks += (progress_bar.get_lock(),)
                    if self.progress_bar is not None:
                        locks += (self.progress_bar.get_lock(),)

                    self.threads_errors[threading.current_thread().name] = error

                    if error_event is not None:
                        error_event.set()
                else:
                    if self.retry_timeout is not None:
                        time.sleep(self.retry_timeout)

                    retry_count += 1

        return (start, position)

    @staticmethod
    def write_to_file(
        lock: threading.Lock,
        io: "FileIO",
        position: int,
        data: bytes,
    ):
        with lock:
            io.seek(position)
            io.write(data)
            io.flush()

    def allocate_downloads(
        self,
        io: "FileIO",
        content_length: int = None,
        connections: int = 8,
        allocate_content_on_disk: bool = False,
        pause_event: "Optional[threading.Event]" = None,
        *,
        start_at: int = 0,
        end_at: int = None,
        threaded: bool = False,
    ):
        error_event = threading.Event()

        if end_at is not None:
            if content_length is None:
                raise ValueError("Cannot specify end_at when content_length is None")
            else:
                content_length = min(content_length, end_at)

        def iter_allocations():
            if not threaded or (
                content_length is None or content_length < self.MINIMUM_PART_SIZE
            ):
                yield None, None
            else:
                chunk_size = (content_length - start_at) // connections
                for i in range(connections - 1):
                    yield start_at + i * chunk_size, start_at + (i + 1) * chunk_size - 1

                yield start_at + (connections - 1) * chunk_size, None

        if allocate_content_on_disk:
            with self.io_lock:
                io.truncate(content_length)

        for n, (start, end) in enumerate(iter_allocations()):
            thread = threading.Thread(
                target=self.download_section,
                args=(io, start, end),
                kwargs={"pause_event": pause_event, "error_event": error_event},
                name=f"{self.__class__.__name__}@0x{id(self):x}-{n}",
            )
            thread.start()
            self.active_threads[thread.name] = thread

        for _, thread in self.active_threads.items():
            thread.join()


def prefetch(
    session: httpx.Client,
    *args,
    **kwargs,
):
    headers = kwargs.pop("headers") or {}
    headers["Range"] = "bytes=0-0"

    with session.stream(*args, **kwargs, headers=headers) as response:
        response.close()
        return response
