import time
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
title {
        romaji
        native
        english
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

    page = 1
    schedules = []

    unix_time = int(time.time())

    data = {}

    while data.get("pageInfo", {}).get("hasNextPage", True):
        schedule_data = client.post(
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
        data = schedule_data.json().get("data", {}).get("Page", {})
        schedules.extend(data.get("airingSchedules", []))
        page += 1

    for date, _content in arrange_template(schedules).items():
        print("On \x1b[33m{}\x1b[39m,".format(date))
        for time_, __content in sorted(
            _content.items(), key=lambda d: d[1][0].get("datetime_object"), reverse=True
        ):
            print(
                "\t\x1b[95m{}\x1b[39m - {}".format(
                    time_,
                    ", ".join(
                        "{anime} [\x1b[94mE{episode}\x1b[39m]".format_map(___content)
                        for ___content in __content
                    ),
                )
            )
