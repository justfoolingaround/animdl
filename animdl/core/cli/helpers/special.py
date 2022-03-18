"""
Special arguments parser
"""

import regex

SPECIAL_PARSER = regex.compile(r"(?P<special>\D+)(-?\d*)", regex.IGNORECASE)

strings = {
    "last": ["l", "latest"],
}


def get_qualified_name(special):
    for key, values in strings.items():
        if special.lower() in (*values, key):
            return key


def special_parser(streams, string):

    returnee = []

    for match in SPECIAL_PARSER.finditer(string):
        special, index = match.group("special", 2)
        index = None if not index else int(index)

        special = get_qualified_name(special)

        if special is None:
            continue

        if special == "last":
            returnee.extend(streams[-(index or 1) :])
        else:
            """
            More specials to be thought about.
            """

    yield from returnee
    yield from (stream for stream in streams if stream not in returnee)
