import functools
import time

API_URL = "https://api.kamyroll.tech"


class Kamyroll:

    API_URL = "https://api.kamyroll.tech/"

    def __init__(self, session):

        self.session = session
        self.raw_token = {}

    def get_token(self):
        expires = self.raw_token.get("expires_in", 0)

        if expires < time.time():

            response = self.session.get(
                self.API_URL + "auth/v1/token",
                params={
                    "device_id": "web",
                    "device_type": "python.animdl",
                    "access_token": "HMbQeThWmZq4t7w",
                },
            )

            self.raw_token = response.json()
        else:
            return f"{self.raw_token['token_type']} {self.raw_token['access_token']}"

        return self.get_token()

    def fetch_seasons(self, media_id, *, channel_id="crunchyroll", locale="en-US"):
        return self.session.get(
            self.API_URL + "content/v1/seasons",
            headers={
                "Authorization": self.get_token(),
            },
            params={"channel_id": channel_id, "id": media_id, "locale": locale},
        ).json()

    def fetch_streams(
        self,
        media_id,
        *,
        channel_id="crunchyroll",
        locale="en-US",
        media_type="adaptive_hls",
    ):
        return self.session.get(
            self.API_URL + "videos/v1/streams",
            params={
                "channel_id": channel_id,
                "locale": locale,
                "id": media_id,
                "type": media_type,
            },
            headers={
                "Authorization": self.get_token(),
            },
        ).json()

    def iter_search_results(self, query, *, channel_id="crunchyroll", locale="en-US"):
        results = self.session.get(
            self.API_URL + "content/v1/search",
            params={
                "channel_id": channel_id,
                "limit": 250,
                "query": query,
            },
            headers={
                "Authorization": self.get_token(),
            },
        ).json()["items"]

        for medias in results:
            for search_results in medias["items"]:
                yield {
                    "title": search_results["title"],
                    "media_id": search_results["id"],
                    "type": medias["type"],
                }

    def fetch_media(self, media_id, *, channel_id="crunchyroll", locale="en-US"):
        return self.session.get(
            self.API_URL + "content/v1/media",
            params={
                "channel_id": channel_id,
                "id": media_id,
                "locale": locale,
            },
            headers={
                "Authorization": self.get_token(),
            },
        ).json()


@functools.lru_cache()
def get_api(session):
    return Kamyroll(session)
