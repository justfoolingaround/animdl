from .fuzzysearch import search

ENDPOINT = "https://api.aniskip.com/v1"

MAL_XHR_SEARCH = "https://myanimelist.net/search/prefix.json"


type_keywords = {
    "op": "Opening",
    "ed": "Ending",
}


def iter_general_timestamps(aniskip_data):

    op_end = None
    ed_start = None

    for item in aniskip_data:

        skip_type = item["skip_type"]

        if skip_type == "op":
            op_end = item["interval"]["end_time"]

        if skip_type == "ed":
            ed_start = item["interval"]["start_time"]

        yield {
            "chapter": type_keywords.get(skip_type, skip_type),
            "start": item["interval"]["start_time"],
            "end": item["interval"]["end_time"],
        }

    if op_end is not None:
        yield {
            "chapter": "Episode",
            "start": op_end,
            "end": ed_start or op_end,
        }

    # NOTE: This is a continuation fix, mpv does not seem to like unmarked chapters between two chapters.


def get_timestamps(session, anime_name, anime_episode):

    data = (
        session.get(
            MAL_XHR_SEARCH,
            params={"type": "anime", "keyword": anime_name},
        )
        .json()
        .get("categories", [{}])[0]
        .get("items", [])
    )

    if not data:
        return

    top_result = (
        tuple(search(anime_name, data, processor=lambda _: _["name"])) or data
    )[0]

    ani_skip_response = session.get(
        f"{ENDPOINT}/skip-times/{top_result['id']}/{anime_episode}",
        params={
            "types[]": ("op", "ed"),
        },
    )

    if ani_skip_response.status_code < 400:
        json_data = ani_skip_response.json()
        if json_data["found"]:
            return list(iter_general_timestamps(json_data["results"]))
