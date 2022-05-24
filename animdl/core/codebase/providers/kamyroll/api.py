import functools
from collections import defaultdict

API_ACCESS_TOKEN = "Basic BCoB9f4m4lSlo+fp05PjlwWcplxQXDT+N+1FfvsyoF41YSy8nH+kuJBQowYrVkiZq6PvTvjFEoQQvzJOt3pJZA=="
CLIENT_REFRESH_TOKEN = "qUwYw6UJ913jR/lWDnTEaTaDDDp2Ft1yvMjcrHTdetK6QboEpAzEsSqf7nvqcCAQsiiGc9dTROkpHgxLOcid5F7IGiXoUv8rbVe/Pnxy0v6//+3iWDKK9kZyltHcvkm6NshhsGq3tLfc6CHvmvZ//RXU9jepqlM/lFMpUq36LWpHvIV/ULZQLnmlfyNBNNiRL0TjKAd33aGfjZa1nYQV4qTHgTxEzc1hHJnUxVZ0Lq7PjeJGRp/ATMgWvActkfzk"


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
