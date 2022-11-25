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
        r"(.*?)".join(map(regex.escape, query.strip())),
        flags=regex.IGNORECASE,
    )

    def genexp():
        for search_value in possibilities:
            match = pattern.search(processor(search_value))
            if match:
                yield len(search_value) - len(query.strip()), search_value

    for _, search_value in sorted(genexp(), key=lambda x: x[0]):
        yield search_value
