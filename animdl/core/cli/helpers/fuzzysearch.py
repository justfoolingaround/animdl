from typing import Callable, Iterable, TypeVar

import regex

search_type = TypeVar("search_type")


def search(
    query: "str",
    possibilities: "Iterable[search_type]",
    *,
    processor: "Callable[[search_type], str]" = lambda r: r
):

    pattern = regex.compile(
        r".*?".join(map(regex.escape, query.strip())) + r".*", flags=regex.IGNORECASE
    )

    for search_value in possibilities:
        if pattern.fullmatch(processor(search_value)):
            yield search_value
