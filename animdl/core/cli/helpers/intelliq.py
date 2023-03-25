"""
IntelliQ, a highly intelligent and robust quality string parser.

Supports:

- best
- 720/1080/2160
- best+subtitles
- titled+>=720[stream_url=r"abc"]
"""


import logging
from collections import namedtuple
from operator import eq, ge, gt, le, lt
from typing import Generator, Iterable, List, Optional, Tuple, TypeVar, Union

from animdl.utils.optopt import regexlib

PARENTHESES = (
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("<", ">"),
    ("«", "»"),
    ("‹", "›"),
    ("『", "』"),
    ("【", "】"),
    ("〖", "〗"),
    ("〘", "〙"),
    ("〚", "〛"),
    ("﴾", "﴿"),
    ("（", "）"),
    ("［", "］"),
    ("｛", "｝"),
    ("《", "》"),
    ("〈", "〉"),
    ("⦗", "⦘"),
    ("⦅", "⦆"),
    ("⦃", "⦄"),
)

QUOTES = ('"', "'")
ESCAPE = "\\"

PORTION_PARSER = regexlib.compile(
    r'(?P<key>.+?)=(?P<regex>r)?("|\')(?P<value>(?:\\\3|.)*?)\3'
)
SEGMENT_PARSER = regexlib.compile(r"(?i)(best|worst|\d+)?(.*)")

QUALITY_REGEX = regexlib.compile(
    r"(?i)\b(?P<expression>[<>=]=?)?(?:\d+x)?(?P<quality>\d+)p?\b"
)

EXPRESSION_MAPPING = {
    ">": gt,
    ">=": ge,
    "<": lt,
    "<=": le,
    "=": eq,
    "==": eq,
}

quality_operator = namedtuple(
    "quality_operator", ("quality", "operator"), defaults=(0, ge)
)


pair_value = TypeVar("pair_value")
stream_type = TypeVar("stream_type")


def remove_parentheses(value, n=None, *, parentheses=PARENTHESES):

    removed_count = 0
    has_parenthesis = True

    while has_parenthesis and (removed_count < n if n is not None else True):

        for start, end in parentheses:
            if value[0:1] == start and value[-1:] == end:
                value = value[1:-1]
                continue

        has_parenthesis = False

    return value


def evaluate_quality_to_number(quality: Optional[Union[str, int]]):
    if quality is None:
        return 0

    if isinstance(quality, int):
        return quality

    if quality.isdigit():
        return int(quality)

    match = QUALITY_REGEX.search(quality)

    if match is None:
        return 0

    return int(match.group("quality"))


def evaluate_quality_to_number_check(quality: Optional[Union[str, int]]):
    if quality is None:
        return quality_operator()

    if isinstance(quality, int):
        return quality_operator(quality, ge)

    if quality.isdigit():
        return quality_operator(int(quality), ge)

    match = QUALITY_REGEX.search(quality)

    if match is None:
        return quality_operator()

    return quality_operator(
        int(match.group("quality")),
        EXPRESSION_MAPPING.get(match.group("expression"), ge),
    )


SPECIAL_SELECTORS = {
    "best": lambda streams: max(
        streams,
        key=lambda stream: evaluate_quality_to_number(stream.get("quality")),
    ),
    "worst": lambda streams: min(
        streams,
        key=lambda stream: evaluate_quality_to_number(stream.get("quality")),
    ),
}

SPECIAL_FILTERS = {
    "subtitles": lambda streams: [
        stream for stream in streams if stream.get("subtitle")
    ],
    "titled": lambda streams: [stream for stream in streams if stream.get("title")],
}


def iter_portions_by(
    string: str,
    splitters: Tuple[str] = ["/"],
    *,
    escape: str = ESCAPE,
    quoters: Tuple[str] = QUOTES,
    parenthesis: Tuple[Tuple[str, str]] = PARENTHESES,
) -> Generator[str, None, None]:
    """
    Separate a string into portions by a list of splitters
    while ignoring the splitters inside quotes and parenthesis.

    When there is a "" in the splitters list, it will return every
    unparenthesized and unquoted portion of the string.
    """

    multiquote_context = dict.fromkeys(quoters, False)
    parenthesis_context = dict.fromkeys(parenthesis, 0)

    escaping = False
    current_context = ""
    yield_this_loop = False

    has_empty_splitter = "" in splitters

    def is_start_of_portion(target: str) -> bool:
        if not target:
            return True

        if any(multiquote_context.values()):
            return False

        if any(parenthesis_context.values()):
            return False

        if target in quoters:
            return True

        pair, is_initiator = get_pair(target, parenthesis)

        if pair in parenthesis_context and is_initiator:
            return True

        return False

    for n, content in enumerate(string):

        portion_ended = False

        pair, is_initiator = get_pair(content, parenthesis)

        if not escaping:
            if content in quoters:
                multiquote_context[content] = not multiquote_context[content]

            if pair in parenthesis_context:
                if is_initiator:
                    parenthesis_context[pair] += 1
                else:
                    parenthesis_context[pair] -= 1

            portion_ended = not (
                any(multiquote_context.values()) or any(parenthesis_context.values())
            )

            is_a_splitter = (
                content in splitters
                and not any(multiquote_context.values())
                and not any(parenthesis_context.values())
            )

            next_character = string[n + 1 : n + 2]
            is_next_new = is_start_of_portion(next_character)

            if (is_a_splitter or portion_ended) and (
                has_empty_splitter and is_next_new
            ):

                if portion_ended or has_empty_splitter:
                    current_context += content

                value = current_context.strip()

                if value:
                    yield value

                yield_this_loop = True

        if yield_this_loop:
            current_context = ""
        else:
            current_context += content

        escaping = content in escape
        yield_this_loop = False

    value = current_context.strip()

    if value:
        yield value


def get_pair(
    target: "pair_value", pairs: Tuple[pair_value, pair_value]
) -> Tuple[Union[Tuple[pair_value, pair_value], Tuple[None, None], bool]]:

    for first, last in pairs:
        if target in (first, last):
            return (first, last), target == first

    return (None, None), False


def iter_fulfilling_streams(
    streams: Iterable[stream_type], quality_string: str, *, all=False
) -> Generator[stream_type, None, None]:

    for segment in iter_portions_by(quality_string):
        """
        Separating "best[subtitles]/best" into "best[subtitles]" and "best"
        """
        candidates = []

        for single_portion in iter_portions_by(segment, splitters=("",)):
            """
            Separating "best[subtitles]" into "best" and "[subtitles]"
            """
            for portion in iter_portions_by(single_portion, splitters=("+",)):
                case_insensitive_portion = portion.lower()

                quality_checker = evaluate_quality_to_number_check(
                    case_insensitive_portion
                )

                for stream in streams:
                    if quality_checker.operator(
                        evaluate_quality_to_number(stream.get("quality")),
                        quality_checker.quality,
                    ):
                        candidates.append(stream)

                if case_insensitive_portion in SPECIAL_FILTERS:
                    candidates = SPECIAL_FILTERS[case_insensitive_portion](candidates)

                portion_match = PORTION_PARSER.search(remove_parentheses(portion))

                if portion_match is not None:
                    portion_key, regex, value = portion_match.group(
                        "key", "regex", "value"
                    )
                    if portion_key in stream:

                        compiled_regex = None

                        if regex is not None:
                            compiled_regex = regexlib.compile(value)

                        candidates = [
                            stream
                            for stream in candidates
                            if (
                                stream[portion_key] == value
                                if compiled_regex is None
                                else compiled_regex.search(stream[portion_key])
                            )
                        ]

                if portion in SPECIAL_SELECTORS:
                    candidates = [SPECIAL_SELECTORS[portion](candidates)]

        for _ in candidates:
            yield single_portion, candidates

        if not all:
            return


def filter_quality(
    streams: Iterable[stream_type], quality_string: str
) -> List[stream_type]:

    logger = logging.getLogger("utils/intelliq")

    portion_map = {}

    for portion, candidates in iter_fulfilling_streams(streams, quality_string):
        portion_map[portion] = candidates

    for portion, candidates in portion_map.items():
        if len(candidates):
            return candidates

    return streams


if __name__ == "__main__":

    test_quality_strings = {
        "best": {
            "values": [
                {"quality": "1080p"},
                {"quality": "720p"},
                {"quality": "480p"},
            ],
            "expected": [{"quality": "1080p"}],
        },
        "worst": {
            "values": [
                {"quality": "1080p"},
                {"quality": "720p"},
                {"quality": "480p"},
            ],
            "expected": [{"quality": "480p"}],
        },
        "=1920x1080p": {
            "values": [
                {"quality": "1080p"},
                {"quality": "720p"},
                {"quality": "480p"},
            ],
            "expected": [{"quality": "1080p"}],
        },
        "=1920x1080p+720p": {
            "values": [
                {"quality": "1080p"},
                {"quality": "720p"},
                {"quality": "480p"},
            ],
            "expected": [{"quality": "1080p"}],
        },
        "subtitles": {
            "values": [
                {"subtitle": [...]},
            ],
            "expected": [{"subtitle": [...]}],
        },
        "[stream_url=r'\.mp4$']": {
            "values": [
                {"stream_url": "abc.mp4"},
                {"stream_url": "abc.mpd"},
            ],
            "expected": [{"stream_url": "abc.mp4"}],
        },
    }

    for test, values in test_quality_strings.items():

        results = filter_quality(values["values"], test)

        assert results == values["expected"], f"{test!r} failed with {results}."

    print("All tests passed.")
