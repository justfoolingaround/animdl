import time
from collections import defaultdict
from datetime import datetime

import click

from ...__version__ import __core__
from ...config import ANICHART, DATE_FORMAT, TIME_FORMAT
from .. import helpers
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
                    userPreferred
                }
            }
        }
    }
}"""


def arrange_template(data):
    template = defaultdict(lambda: defaultdict(list))

    for airing in data[::-1]:
        datetime_object = datetime.fromtimestamp(airing.get("airingAt", 0))
        template[format(datetime_object, DATE_FORMAT)][
            (format(datetime_object, TIME_FORMAT), datetime_object)
        ].append(
            {
                "name": airing.get("media", {}).get("title", {}).get("userPreferred"),
                "episode": airing.get("episode", 0),
            }
        )
    return template


def iter_schedules(session, unix_time):
    page = 1

    data = {}

    week_end = unix_time + 24 * 7 * 60 * 60

    while data.get("pageInfo", {}).get("hasNextPage", True):
        schedule_data = session.post(
            ANICHART,
            json={
                "query": gql,
                "variables": {
                    "weekStart": unix_time,
                    "weekEnd": week_end,
                    "page": page,
                },
            },
        )

        data = schedule_data.json().get("data", {}).get("Page", {})
        page += 1

        yield from data.get("airingSchedules", [])


@click.command(name="schedule", help="Know which animes are going over the air when.")
@helpers.decorators.logging_options()
@helpers.decorators.setup_loggers()
@helpers.decorators.banner_gift_wrapper(client, __core__)
def animdl_schedule(**kwargs):

    for date_format, child_component in arrange_template(
        list(iter_schedules(client, int(time.time())))
    ).items():
        click.secho(f"On {date_format}", fg="cyan")
        for (time_format, _), anime_components in sorted(
            child_component.items(), key=lambda component: component[0][1], reverse=True
        ):
            click.echo(
                f"\t{click.style(time_format, fg='magenta')} - {{}}".format(
                    ", ".join(
                        f"{anime['name']} [{click.style(anime['episode'], fg='blue')}]"
                        for anime in anime_components
                    ),
                )
            )
