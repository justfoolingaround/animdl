"""
animdl: Utility functions for caching HTTP requests.
"""

import atexit
import os
import pathlib
import sqlite3
import time
from datetime import timedelta
from urllib.parse import urlencode

import httpx

from .optopt import jsonlib, regexlib

caching_mimetypes = {
    "application": {
        "json",
        "xml",
        "x-www-form-urlencoded",
        "x-javascript",
        "javascript",
    },
    "text": {"html", "css", "javascript", "plain", "xml", "xsl", "x-javascript"},
}


class CachingHTTPXClient(httpx.Client):
    """
    HTTPX client with caching capabilities.

    :param cache_db_path: The path to the cache database.
    :param cache_db_lock_file: The path to the cache database lock file.
    :param max_lifetime: The maximum lifetime of a cache entry.
    :param max_size: The maximum size of the cache database.
    :param table_name: The name of the table to use for the cache.

    This class adds a middleware to the HTTPX client that
    caches the responses to an sqlite3 database.

    The cache database is a single table with the following
    columns:

    - url: The URL of the request.
    - status_code: The status code of the response.
    - request_headers: The request headers of the request.
    - response_headers: The response headers of the response.
    - data: The data of the response.
    - redirection_policy: The redirection policy of the request.
    - cache_expiry: The expiry time of the cache entry.

    Usage:

    >>> from animdl.utils.http_caching import CachingHTTPXClient
    >>> import time
    >>> client = CachingHTTPXClient("cache.db", "cache.lock")
    >>> initial_time = time.time()
    >>> client.get("https://example.com")
    <Response [200 OK]>
    >>> print("Request took:", time.time() - initial_time)
    >>> initial_time = time.time()
    >>> client.get("https://example.com")
    <Response [200 OK]>
    >>> print("Cached request took:", time.time() - initial_time)
    """

    request_functions = (
        "get",
        "options",
        "head",
        "post",
        "put",
        "patch",
        "delete",
    )

    def __new__(cls, *args, **kwargs):
        def caching_params(name: str):
            def wrapper(self, *args, **kwargs):
                return cls.request(self, name.upper(), *args, **kwargs)

            return wrapper

        for func in cls.request_functions:
            setattr(cls, func, caching_params(func))

        return super().__new__(cls)

    def __init__(
        self,
        cache_db_path: str,
        cache_db_lock_file: str,
        max_lifetime: int = 604800,
        max_size: int = (1024**2) * 10,
        table_name: str = "animdl_http_cache",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.cache_db_path = cache_db_path
        self.max_lifetime = max_lifetime
        self.max_size = max_size
        self.connection = sqlite3.connect(self.cache_db_path)
        self.table_name = table_name

        self.connection.cursor().execute(
            f"create table if not exists {self.table_name!r} ("
            "url text, "
            "status_code integer, "
            "request_headers text, "
            "response_headers text, "
            "data blob,"
            "redirection_policy int,"
            "cache_expiry integer"
            ")",
        )

        atexit.register(lambda conn: conn.commit() or conn.close(), self.connection)
        self.setup_lockfile(cache_db_lock_file)

    def request(
        self,
        method,
        url,
        params=None,
        force_caching=False,
        fresh=False,
        *args,
        **kwargs,
    ):

        if fresh:
            return super().request(method, url, params=params, *args, **kwargs)

        if params is not None:
            url += "?" + urlencode(params)

        redirection_policy = int(kwargs.get("force_redirects", False))
        cursor = self.connection.cursor()

        cursor.execute(
            "select "
            "status_code, "
            "request_headers, "
            "response_headers, "
            "data, "
            "redirection_policy "
            f" from {self.table_name!r} where url = ? and redirection_policy = ? and cache_expiry > ?",
            (url, redirection_policy, int(time.time())),
        )

        result = cursor.fetchone()

        if result is not None:
            (
                status_code,
                request_headers,
                response_headers,
                data,
                redirection_policy,
            ) = result

            response = httpx.Response(
                status_code=status_code,
                headers=jsonlib.loads(response_headers),
                content=data,
                request=httpx.Request(
                    method, url, headers=jsonlib.loads(request_headers), *args, **kwargs
                ),
            )
            response.elapsed = timedelta(seconds=0)
            return response

        response = super().request(method, url, *args, **kwargs)

        if response.status_code < 400 and (
            force_caching
            or self.is_content_type_cachable(
                response.headers.get("content-type"), caching_mimetypes
            )
            and len(response.content) < self.max_size
        ):

            cursor.execute(
                f"insert into {self.table_name!r} values (?, ?, ?, ?, ?, ?, ?)",
                (
                    url,
                    response.status_code,
                    jsonlib.dumps(dict(response.request.headers)),
                    jsonlib.dumps(dict(response.headers)),
                    response.content,
                    redirection_policy,
                    int(time.time()) + self.max_lifetime,
                ),
            )

            self.connection.commit()

        return response

    @staticmethod
    def is_content_type_cachable(content_type, caching_mimetypes):
        if content_type is None:
            return True

        mime, contents = content_type.split("/")

        contents = regexlib.sub(r";.*$", "", contents)

        return mime in caching_mimetypes and any(
            content in caching_mimetypes[mime] for content in contents.split("+")
        )

    @staticmethod
    def setup_lockfile(lock_file: str):
        lockfile_path = pathlib.Path(lock_file)

        if lockfile_path.exists():
            with lockfile_path.open("r") as f:
                pid = f.read()

            raise RuntimeError(
                f"This instance of {__class__.__name__!r} is already running with PID: {pid}. "
                "Sqlite3 does not support multiple connections to the same database. "
                "If you are sure that no other instance of this class is running, "
                f"delete the lock file at {lockfile_path.as_posix()!r} and try again."
            )

        with lockfile_path.open("w") as f:
            f.write(str(os.getpid()))

        atexit.register(lockfile_path.unlink)


if __name__ == "__main__":
    client = CachingHTTPXClient("cache.db", "cache.lockfile")

    print(
        client.get(
            "https://google.com",
        ).elapsed
    )

    print(
        client.get(
            "https://google.com",
        ).elapsed
    )
