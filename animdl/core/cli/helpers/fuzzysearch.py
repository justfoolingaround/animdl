from typing import Callable, Iterable, TypeVar

import regex

search_type = TypeVar("search_type")

options = {
    "ignore_whitespace": lambda x: regex.sub(r"\s+", "", x),
    "ignore_punctuation": lambda x: regex.sub(r"\p{P}+", "", x),
}


def search(
    query: "str",
    possibilities: "Iterable[search_type]",
    *,
    processor: "Callable[[search_type], str]" = lambda r: r,
    search_options: tuple = ("ignore_punctuation",),
):

    pattern = regex.compile(
        r"(.*?)".join(map(regex.escape, query.strip())),
        flags=regex.IGNORECASE,
    )

    def genexp():
        for search_value in possibilities:
            processed_search_value = processor(search_value)

            for option in search_options:
                if option in options:
                    processed_search_value = options[option](processed_search_value)

            match = pattern.search(processed_search_value)
            if match:
                yield len(processed_search_value) - len(query.strip()), search_value

    for _, search_value in sorted(genexp(), key=lambda x: x[0]):
        yield search_value
