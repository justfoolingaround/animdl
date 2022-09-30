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
        r"(.*?)".join(map(regex.escape, query.strip())) + r"(.*)",
        flags=regex.IGNORECASE,
    )

    def genexp():
        for search_value in possibilities:
            match = pattern.fullmatch(processor(search_value))
            if match:
                yield sum(len(_) for _ in match.groups()), search_value

    for _, search_value in sorted(genexp(), key=lambda x: x[0]):
        yield search_value
