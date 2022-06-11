import functools
from collections import defaultdict

API_ACCESS_TOKEN = "Basic vrvluizpdr2eby+RjSKM17dOLacExxq1HAERdxQDO6+2pHvFHTKKnByPD7b6kZVe1dJXifb6SG5NWMz49ABgJA=="
CLIENT_REFRESH_TOKEN = "vDruXuycqziQocWmI8irARTQa9txXvUKW/LQpGjklYNN1wwJ1dL9KtG19IjPgJVcwSbJ8zUIhlaR4W+IlmY3xiJZ+9nefH4RF4ugWvGWPFq1Q2mcJfxStP/qxfdln2K4UqfOqSjTC/Q8gekarRa9n+fdjUqum6YSV18Coz8gUDQoCTh2ljBwF5mtYZIXGxFn3zC2t8GANTGtmViOLxNNF1axa/m2Rgo8aC3B/tiX+Hg6brP2LtCR/EY0P5IHOB5xClUh1/xqTdD4U4NkYEdfrFB/JZ33+vu/pUHrM/Fa0u7qH6X8w/UtBMkfz/LVOCd8pMgrziOYX+oQTyhFcYncJSaoTsR8V0uEQDu6Z9rkR/xIAe8vq4T8D/PMFOFmgIaDN2UG/Rfh0167Esn9D1PmT8wOyPKeTgmlRuXwwJehn3o="


@functools.lru_cache()
def fetch_api_grant_token(session, api_endpoint):
    return "%(token_type)s %(access_token)s" % (
        session.post(
            api_endpoint + "auth/v1/token",
            data={
                "refresh_token": CLIENT_REFRESH_TOKEN,
                "grant_type": "refresh_token",
                "scope": "all",
            },
            headers={
                "Authorization": API_ACCESS_TOKEN,
            },
        ).json()
    )


def fetch_seasons(session, api_endpoint, media_id, *, predicate=None):
    media = session.get(
        api_endpoint + "content/v1/seasons",
        headers={
            "Authorization": fetch_api_grant_token(session, api_endpoint),
        },
        params={"channel_id": "crunchyroll", "id": media_id, "locale": "en-US"},
    ).json()

    episodes = defaultdict(list)

    for season in media.get("items", []):
        for episode in season.get("episodes", []):
            if predicate is None or predicate(episode):
                episodes[episode["episode_number"]].append(episode)

    return episodes


def get_media_streams(
    session,
    api_endpoint,
    media_id,
    *,
    channel_id="crunchyroll",
    locale="en-US",
    media_type="adaptive_hls"
):
    return session.get(
        api_endpoint + "videos/v1/streams",
        params={
            "channel_id": channel_id,
            "locale": locale,
            "id": media_id,
            "type": media_type,
        },
        headers={
            "Authorization": fetch_api_grant_token(session, api_endpoint),
        },
    ).json()
