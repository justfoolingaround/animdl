"""
animdl: Utilities for the internal searching system. 
"""
import string
from typing import Callable, Iterable, Optional, TypeVar

from .optopt import regexlib

search_type = TypeVar("search_type")


options = {
    "ignore_whitespace": lambda x: regexlib.sub(r"\s+", "", x),
    "ignore_punctuation": lambda x: regexlib.sub(
        rf"[{regexlib.escape(string.punctuation)}]+", "", x
    ),
}


def iter_search_results(
    query: str,
    possibilities: Iterable[search_type],
    *,
    processor: Optional[Callable[[search_type], str]] = None,
    search_options: Iterable[str] = ("ignore_punctuation",),
):
    """
    Powerful searching function that uses regex building
    for matching the query with the possibilities.

    :param query: The query to search for.
    :param possibilities: The possibilities to search in.
    :param processor: A function that processes the possibilities.
    :param search_options: The options to use for searching.

    :return: A generator that yields the search results.
    """
    pattern = regexlib.compile(
        r"(.*?)".join(map(regexlib.escape, query.strip())),
        flags=regexlib.IGNORECASE,
    )

    def genexp():
        for search_value in possibilities:
            if processor is not None:
                processed_value = processor(search_value)
            else:
                processed_value: str = search_value  # type: ignore

            for option in search_options:
                if option in options:
                    search_value = options[option](search_value)

            match = pattern.search(processed_value)

            if match:
                yield len(processed_value), search_value

    for _, search_value in sorted(genexp(), key=lambda x: x[0]):
        yield search_value
