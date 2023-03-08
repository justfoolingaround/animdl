from animdl.utils import optopt

ENDPOINT = "https://api.allanime.co/allanimeapi"

ALLANIME_SEARCH_GQL = """\
query(
        $search: SearchInput
        $limit: Int
        $page: Int
        $translationType: VaildTranslationTypeEnumType
        $countryOrigin: VaildCountryOriginEnumType
    ) {
    shows(
        search: $search
        limit: $limit
        page: $page
        translationType: $translationType
        countryOrigin: $countryOrigin
    ) {
        pageInfo {
            total
        }
        edges {
            %s
        }
    }
}"""


ALLANIME_EPISODES_GQL = """\
query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {
    episode(
        showId: $showId
        translationType: $translationType
        episodeString: $episodeString
    ) {
        %s
    }
}"""

ALLANIME_SHOW_GQL = """
query ($showId: String!) {
    show(
        _id: $showId
    ) {
        %s
    }
}
"""


class AllAnimeGQLAPI:
    """
    Fast and effective GQL API wrapper for AllAnime.
    """

    info_table = {}

    def __init__(self, *, endpoint: str = ENDPOINT):
        self.api_endpoint = endpoint

    def fetch_gql(
        self,
        session,
        query: str,
        variables: dict = None,
    ):

        response = session.get(
            self.api_endpoint,
            params={
                "variables": optopt.jsonlib.dumps(variables),
                "query": query,
            },
        ).json()

        if response.get("errors"):
            return {}

        return response.get("data", {})

    def iter_search_results(
        self,
        session,
        query: str,
        translation_type=None,
        country_origin=None,
        show_nsfw=True,
        show_unknown=True,
        limit=None,
        *,
        keys: tuple = (
            "_id",
            "name",
            "availableEpisodesDetail",
        ),
    ):
        search = {
            "allowAdult": show_nsfw,
            "allowUnknown": show_unknown,
            "query": query,
        }

        variables = {
            "search": search,
        }

        if translation_type is not None:
            variables["translationType"] = translation_type

        if country_origin is not None:
            variables["countryOrigin"] = country_origin

        current_count = 0
        total = None
        page = 1

        gql = ALLANIME_SEARCH_GQL % " ".join(keys)

        while limit is None or current_count < limit:
            variables["page"] = page
            variables["limit"] = limit or 40

            response = self.fetch_gql(session, gql, variables)

            edges = response.get("shows", {}).get("edges", [])

            if not edges:
                return

            for data in edges:

                self.info_table.setdefault(data["_id"], {}).update(data)

                yield data

            current_count += len(edges)
            page += 1

            total = total or (
                response.get("shows", {}).get("pageInfo", {}).get("total", limit)
            )
            if limit is None:
                limit = total

    def fetch_show_info(
        self,
        session,
        show_id: str,
        keys: tuple = (
            "_id",
            "name",
            "availableEpisodesDetail",
        ),
    ):
        if show_id in self.info_table and (
            keys is None or all(key in self.info_table[show_id] for key in keys)
        ):
            return self.info_table[show_id]

        variables = {
            "showId": show_id,
        }

        response = self.fetch_gql(
            session,
            ALLANIME_SHOW_GQL % " ".join(keys),
            variables,
        )

        self.info_table.setdefault(show_id, {}).update(response.get("show", {}))

        return response.get("show", {})

    def fetch_episode(
        self,
        session,
        show_id: str,
        episode_string: str,
        *,
        translation_type: str = "sub",
        keys: tuple = ("episodeString", "sourceUrls", "notes"),
    ):
        variables = {
            "showId": show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }

        return self.fetch_gql(
            session, ALLANIME_EPISODES_GQL % " ".join(keys), variables
        )


api = AllAnimeGQLAPI()
