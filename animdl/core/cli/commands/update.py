import logging
import pathlib
import shutil
import subprocess
import sys

import click
import pip
import regex

from ...__version__ import __core__
from .. import helpers, http_client

GIT_CONFIG_REPO_NAME = regex.compile(
    r'\[remote ".+?"\].+?url = (\S+)', flags=regex.S
)


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

    if is_repository(*helpers.constants.SOURCE_REPOSITORY):
        update_logger = logging.getLogger(f"updater/git")

        if not shutil.which("git"):
            return update_logger.error("Couldn't find git to attempt.")

        process = subprocess.Popen(
            ["git", "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    else:

        update_logger = logging.getLogger(f"updater/pip v{pip.__version__}")

        upstream_version = helpers.banner.fetch_upstream_version(http_client.client)
        tuplised_upstream, tuplised_current_version = tuple(
            upstream_version.split(".")
        ), tuple(__core__.split("."))

        comparison, description = helpers.banner.compare_version(
            tuplised_current_version, tuplised_upstream
        )

        if description is not None:
            update_logger.info(description)

        if not comparison:
            return update_logger.error("Already up to date.")

        update_logger.info(
            f"Updating module {helpers.constants.MODULE_NAME!r} via PIP: pip install --upgrade {helpers.constants.MODULE_NAME}"
        )

        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                helpers.constants.MODULE_NAME,
                "--user",
                "--no-warn-script-location",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    for line in process.stdout:
        update_logger.info(f"[stdout] {line.decode().rstrip()}")

    for line in process.stderr:
        update_logger.error(f"[stderr] {line.decode().rstrip()}")
