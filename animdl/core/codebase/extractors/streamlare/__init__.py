import lxml.html as htmlparser
import regex

STREAMLARE = "https://streamlare.com/"

CONTENT_ID = regex.compile(r"/[ve]/([^?#&/]+)")


def extract(session, url, **opts):

    csrf_token = (
        htmlparser.fromstring(session.get(url).text)
        .cssselect("meta[name='csrf-token']")[0]
        .get("content")
    )
    content_id = CONTENT_ID.search(url).group(1)

    def fast_yield():
        for _, streams in (
            session.post(
                STREAMLARE + "api/video/get",
                headers={
                    "x-requested-with": "XMLHttpRequest",
                    "x-csrf-token": csrf_token,
                },
                json={"id": content_id},
            )
            .json()
            .get("result")
            .items()
        ):
            yield {"stream_url": streams.get("src"), "headers": {"referer": STREAMLARE}}

    return list(fast_yield())
