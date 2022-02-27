from collections import defaultdict
from datetime import datetime

import click

from ...config import ANICHART, DATE_FORMAT, TIME_FORMAT
from ..helpers import bannerify
from ..http_client import client


gql = """query (
        $weekStart: Int,
        $weekEnd: Int,
        $page: Int,
){
        Page(page: $page) {
                pageInfo {
                        hasNextPage
                        total
                }
                airingSchedules(
                        airingAt_greater: $weekStart
                        airingAt_lesser: $weekEnd
                ) {
                        id
                        episode
                        airingAt
                        media {

id
idMal
title {
        romaji
        native
        english
}
startDate {
        year
        month
        day
}
endDate {
        year
        month
        day
}
status
season
format
genres
synonyms
duration
popularity
episodes
source(version: 2)
countryOfOrigin
hashtag
averageScore
siteUrl
description
bannerImage
isAdult
coverImage {
        extraLarge
        color
}
trailer {
        id
        site
        thumbnail
}
externalLinks {
        site
        url
}
rankings {
        rank
        type
        season
        allTime
}
studios(isMain: true) {
        nodes {
                id
                name
                siteUrl
        }
}
relations {
        edges {
                relationType(version: 2)
                node {
                        id
                        title {
                                romaji
                                native
                                english
                        }
                        siteUrl
                }
        }
}


                        }
                }
        }
}"""


def arrange_template(data):
    content = defaultdict(lambda: defaultdict(list))

    for airing in data[::-1]:
        dtobj = datetime.fromtimestamp(airing.get("airingAt", 0))
        d, t = dtobj.strftime(DATE_FORMAT), dtobj.strftime(TIME_FORMAT)
        titles = airing.get("media", {}).get("title", {})
        content[d][t].append(
            {
                "anime": titles.get("english")
                or titles.get("romaji")
                or titles.get("native"),
                "episode": airing.get("episode", 0),
                "datetime_object": dtobj,
            }
        )

    return content


@click.command(name="schedule", help="Know which animes are going over the air when.")
@click.option(
    "--log-file",
    help="Set a log file to log everything to.",
    required=False,
)
@click.option(
    "-ll", "--log-level", help="Set the integer log level.", type=int, default=20
)
@bannerify
def animdl_schedule(**kwargs):

    has_next_page, page = True, 1
    schedules = []
    session = client

    unix_time = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

    while has_next_page:
        schedule_data = session.post(
            ANICHART,
            json={
                "query": gql,
                "variables": {
                    "weekStart": unix_time,
                    "weekEnd": unix_time + 24 * 7 * 60 * 60,
                    "page": page,
                },
            },
        )
        data = schedule_data.json()
        schedules.extend(
            data.get("data", {}).get("Page", {}).get("airingSchedules", [])
        )
        has_next_page = (
            data.get("data", {})
            .get("Page", {})
            .get("pageInfo", {})
            .get("hasNextPage", False)
        )
        page += 1

    for date, _content in arrange_template(schedules).items():
        print("On \x1b[33m{}\x1b[39m,".format(date))
        for time, __content in sorted(
            _content.items(), key=lambda d: d[1][0].get("datetime_object"), reverse=True
        ):
            print(
                "\t\x1b[95m{}\x1b[39m - {}".format(
                    time,
                    ", ".join(
                        "{anime} [\x1b[94mE{episode}\x1b[39m]".format_map(___content)
                        for ___content in __content
                    ),
                )
            )
