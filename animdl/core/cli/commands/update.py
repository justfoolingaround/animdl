import asyncio
import pathlib
import shlex
import shutil
import sys

import click
import regex

from ...__version__ import __core__
from .. import helpers

GIT_CONFIG_REPO_NAME = regex.compile(r'\[remote ".+?"\].+?url = (\S+)', flags=regex.S)


def is_repository(author, repository):

    if not pathlib.Path("./.git/").exists():
        return False

    repository_qualname = f"{author}/{repository}"

    with open("./.git/config") as git_config:
        match = GIT_CONFIG_REPO_NAME.search(git_config.read())

        if match is None:
            return False

    return match.group(1)[-len(repository_qualname) :] == repository_qualname


@click.command("update", help="Update the project or git pull if a repository.")
@helpers.decorators.setup_loggers()
def animdl_update(*args, **kwargs):

    console = helpers.stream_handlers.get_console()

    with helpers.stream_handlers.context_raiser(
        console,
        helpers.stream_handlers.Text(
            f"Updating {helpers.constants.MODULE_NAME!r}",
            style="bold white",
        ),
        name="update",
    ):

        executable = None

        async def __asyncio__():

            if is_repository(*helpers.constants.SOURCE_REPOSITORY):

                executable = shutil.which("git")
                args = [
                    executable,
                    "pull",
                ]

                console.print(
                    f"Pulling latest changes from the repository via git: {shlex.join(args)}"
                )

                if not executable:
                    return console.print("[red]Cannot find git.[/]")

                process = await asyncio.subprocess.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

            else:

                executable = sys.executable

                args = [
                    executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    helpers.constants.MODULE_NAME,
                    "--user",
                    "--no-warn-script-location",
                ]

                console.print(
                    f"Updating module {helpers.constants.MODULE_NAME!r} via PIP: {shlex.join(args)}"
                )

                process = await asyncio.subprocess.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

            async def async_stream_reader(stream, style, name):

                line = await stream.readline()
                while line:
                    console.print(
                        helpers.stream_handlers.Text(name, style=style),
                        helpers.stream_handlers.Text(line.decode().strip()),
                    )
                    line = await stream.readline()

            await asyncio.gather(
                async_stream_reader(process.stdout, "green", f"[{executable} stdout]"),
                async_stream_reader(process.stderr, "red", f"[{executable} stderr]"),
            )

        loop = asyncio.new_event_loop()
        loop.run_until_complete(__asyncio__())
