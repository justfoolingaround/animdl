import functools
import time

import pypresence

ANIMDL_APPLICATION_ID = 897850955373105222

try:
    presence_client = pypresence.Presence(ANIMDL_APPLICATION_ID)
except (pypresence.DiscordNotFound, ConnectionError):
    raise RuntimeError("Could not connect to Discord.")

presence_client.connect()

presence_client.update(
    state="Queuing up the streams",
    large_image="mascot",
    large_text="https://github.com/justfoolingaround/animdl",
)

KITSU_ENDPOINT = "https://kitsu.io/api/"


@functools.lru_cache()
def get_anime(session, anime_name):
    return session.get(
        KITSU_ENDPOINT + "edge/anime", params={"filter[text]": anime_name}
    ).json()["data"]


@functools.lru_cache()
def get_episodes(session, anime_id, offset):

    params = {
        "filter[media_id]": anime_id,
        "sort": "number",
        "filter[mediaType]": "Anime",
        "page[limit]": 10,
    }

    if offset is not None and offset > 1:
        params["page[offset]"] = offset

    return session.get(KITSU_ENDPOINT + "edge/episodes", params=params).json()["data"]


def set_streaming_episode(session, anime_name, episode):

    state = anime_name

    if episode:
        state += " - Episode {}".format(episode)

    content_list = get_anime(session, anime_name)

    if not content_list:
        return presence_client.update(
            state=state,
            large_image="mascot",
            large_text="https://github.com/justfoolingaround/animdl",
            start=int(time.time()),
        )

    anime = content_list[0]

    anime_attributes = anime["attributes"]

    image = anime_attributes["posterImage"]["original"]
    count = anime_attributes["episodeCount"]
    url = "https://kitsu.io/{}/{}".format(anime['type'], anime_attributes['slug'])
    url_button = [ { "label": "View Anime", "url": url } ]

    if count:
        state += "/{}".format(count)

    if count is None or (episode > count):
        return presence_client.update(
            state=state,
            large_image=image,
            large_text=anime_name,
            small_image="mascot",
            small_text="https://github.com/justfoolingaround/animdl",
            start=int(time.time()),
            buttons=url_button,
        )

    around = episode - (episode % 10)

    current = get_episodes(session, anime["id"], around)[episode % 10 - 1]

    episode_name = current.get("attributes", {}).get("canonicalTitle")
    episode_thumbnail = (current.get("attributes", {}).get("thumbnail", {}) or {}).get(
        "original", "mascot"
    )

    if episode_thumbnail == "mascot":
        image, episode_thumbnail = episode_thumbnail, image

    return presence_client.update(
        state=state,
        large_image=episode_thumbnail,
        large_text=episode_name if image != "mascot" else anime_name,
        small_image=image,
        small_text=anime_name if image != "mascot" else "https://github.com/justfoolingaround/animdl",
        details=episode_name,
        start=int(time.time()),
        buttons=url_button,
    )
