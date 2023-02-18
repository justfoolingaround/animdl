"""
A one cli for all the anime.
"""

import os
import random
import sys

import click
from rich.align import Align
from rich.style import Style
from rich.text import Text
from rich.traceback import install

from .core import __version__
from .core.cli.commands import download, grab, schedule, search, stream, update
from .core.cli.helpers import stream_handlers

install(show_locals=True, suppress=[click])

commands = {
    "download": download.animdl_download,
    "grab": grab.animdl_grab,
    "schedule": schedule.animdl_schedule,
    "search": search.animdl_search,
    "update": update.animdl_update,
    "stream": stream.animdl_stream,
}


@click.group(commands=commands, invoke_without_command=True)
@click.version_option(__version__.__core__, "--version")
@click.option("-x", "--disable-update", is_flag=True, help="Disable update check.")
@click.pass_context
def __animdl_cli__(ctx: click.Context, disable_update):
    from .core.cli.helpers import constants

    sys.stderr = sys.__stderr__
    console = stream_handlers.get_console()

    if ctx.invoked_subcommand is None:
        console.print(
            "The project is operational. Use --help flag for help & be sure read the documentation!"
        )

    author, repository_name = constants.SOURCE_REPOSITORY

    console.print(
        Align(
            Text(
                f"{author}/{repository_name} v{__version__.__core__}",
                style="magenta",
            ),
            align="center",
        )
    )

    with stream_handlers.context_raiser(
        console,
        Text(
            f"{random.choice(('Hey', 'Hello', 'Welcome'))}, {os.getenv('USERNAME', 'buddy')}.",
            style="bold white",
        ),
    ):
        for greeting in stream_handlers.iter_greetings():
            console.print(greeting, style="white")

        if not disable_update:
            from animdl.utils.optopt import regexlib

            from .core.cli.http_client import client

            branch, version_file = constants.VERSION_FILE_PATH

            upstream_version = regexlib.search(
                r'__core__ = "(.*?)"',
                client.get(
                    f"https://raw.githubusercontent.com/{author}/{repository_name}/{branch}/{version_file}"
                ).text,
            ).group(1)

            tuplisied_upstream, tuplised_current_version = tuple(
                map(int, upstream_version.split("."))
            ), tuple(map(int, __version__.__core__.split(".")))

            if tuplisied_upstream > tuplised_current_version:
                with stream_handlers.context_raiser(
                    console, "[cyan]An update is available![/]"
                ):
                    console.print(
                        f"↑ {upstream_version} ↓ {__version__.__core__}, to update, use: animdl update",
                        style=Style(color="magenta"),
                    )
                    console.print(
                        f"Staying up-to-date resolves bugs and security vulnerabilities!",
                        style="dim i",
                    )


if __name__ == "__main__":
    __animdl_cli__()
