import regex
import yarl

from ...helper import uwu

CONTENT_ID_REGEX = regex.compile(r"embed-6/([^?#&/.]+)")


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

    def yielder():
        for _ in sources.get("sources"):
            yield {"stream_url": _.get("file"), "subtitle": subtitles}

        for _ in sources.get("sourcesBackup"):
            yield {"stream_url": _.get("file"), "subtitle": subtitles}

    return list(yielder())
