import regex

STREAMLARE = "https://streamlare.com/"

CONTENT_ID = regex.compile(r"/e/([^?#&/]+)")


def extract(session, url, **opts):

    content_id = CONTENT_ID.search(url).group(1)

    def fast_yield():
        for _, streams in (
            session.post(
                STREAMLARE + "api/video/get",
                headers={"x-requested-with": "XMLHttpRequest"},
                json={"id": content_id},
            )
            .json()
            .get("result")
            .items()
        ):
            yield {"stream_url": streams.get("src"), "headers": {"referer": STREAMLARE}}

    return list(fast_yield())
