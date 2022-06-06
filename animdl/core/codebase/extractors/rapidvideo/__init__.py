import threading

import regex
import yarl

from ...helper import uwu

CONTENT_ID_REGEX = regex.compile(r"embed-6/([^?#&/.]+)")


parent_thread = threading.current_thread()

sid_holder = {
    "sid": None,
}

active_event = threading.Event()


def extract(session, url, **opts):

    from .polling import ws_stimulation

    if sid_holder["sid"] is None and not active_event.is_set():
        active_event.set()

        threading.Thread(
            target=ws_stimulation,
            kwargs={
                "session": session,
                "close_event": active_event,
                "sid_holder": sid_holder,
                "parent_thread": parent_thread,
            },
        ).start()

    while sid_holder["sid"] is None:
        pass

    sid = sid_holder["sid"]

    content_id = CONTENT_ID_REGEX.search(url).group(1)
    recaptcha_response = uwu.bypass_recaptcha(session, url, opts["headers"])

    ajax_response = session.get(
        "https://{}/ajax/embed-6/getSources".format(yarl.URL(url).host),
        params={
            "id": content_id,
            "_token": recaptcha_response.get("token", ""),
            "_number": recaptcha_response.get("number", ""),
        },
    )

    sources = ajax_response.json()

    subtitles = [
        _.get("file") for _ in sources.get("tracks") if _.get("kind") == "captions"
    ]

    def yielder():
        for _ in sources.get("sources"):
            yield {
                "stream_url": _.get("file"),
                "subtitle": subtitles,
                "headers": {"SID": sid},
            }

        for _ in sources.get("sourcesBackup"):
            yield {
                "stream_url": _.get("file"),
                "subtitle": subtitles,
                "headers": {"SID": sid},
            }

    return list(yielder())
