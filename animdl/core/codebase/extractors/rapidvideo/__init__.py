from functools import lru_cache

import regex
import yarl

from ...helper import uwu

CONTENT_ID_REGEX = regex.compile(r"embed-6/([^?#&/.]+)")

SID_REGEX = regex.compile(r'"sid":"(.+?)"')

POLLING_PARAMETERS = {
    "EIO": "4",
    "transport": "polling",
}


@lru_cache()
def ws_stimulation(session, *, url="https://ws1.rapid-cloud.ru/socket.io/"):
    def poll(params={}, data=None):
        soft = POLLING_PARAMETERS.copy()
        soft.update(params)

        if data is None:
            return session.get(url, params=soft)
        else:
            return session.post(url, params=soft, data=data)

    def get_sid(text: str) -> str:
        return SID_REGEX.search(text).group(1)

    polling_sid = get_sid(poll().text)

    assert poll({"sid": polling_sid}, data="40").text == "ok"

    return get_sid(poll({"sid": polling_sid}).text)


def extract(session, url, **opts):

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

    sid = ws_stimulation(session)

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
