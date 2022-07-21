"""
For when animixplay does not know
but the project knows.
"""

from functools import partial

import regex

REPL_REGEX = regex.compile(r"'(.+?)'")


hard_urls = {
    "overflow": {
        "provider": "bestcdn",
        "streams": [(f"Overflow/Overflow {_:02d}.mp4", _) for _ in range(1, 9)],
    },
    "jimihen-jimiko-wo-kaechau-jun-isei-kouyuu": {
        "provider": "bestcdn",
        "streams": [(f"Jimihen/Jimihen {_:02d}.mp4", _) for _ in range(1, 9)],
    },
}


def yield_from_bestcdn(session, attributes):

    repl_string = REPL_REGEX.search(
        session.get("https://anfruete.github.io/play/env.js").text
    ).group(1)

    for stream, episode in attributes["streams"]:
        yield partial(
            lambda stream: [{"stream_url": f"https://{repl_string}/{stream}"}], stream
        ), episode


yielder_mapping = {
    "bestcdn": yield_from_bestcdn,
}


def get_hardstream_generator(session, hard_stream):

    if hard_stream not in hard_urls:
        return

    attrs = hard_urls[hard_stream]
    provider = attrs["provider"]

    if provider not in yielder_mapping:
        return

    yielder = yielder_mapping[provider]
    return yielder(session, attrs)
