import shutil

import click
import regex
from anchor.strings import iter_contentaware_segments

from .constants import SOURCE_REPOSITORY, VERSION_FILE_PATH

terminal_columns = shutil.get_terminal_size((0, 0)).columns

VERSION_REGEX = regex.compile(r'__core__ = "(.*?)"')


def iter_banner(
    session,
    current_version,
    *,
    check_for_updates=True,
    description="A highly efficient, powerful and fast anime scraper.",
):

    author, repository_name = SOURCE_REPOSITORY

    if terminal_columns:
        processor = lambda _: iter_contentaware_segments(
            str.center(_, terminal_columns), terminal_columns
        )
    else:
        processor = lambda _: iter((_,))

    yield from processor(
        click.style(f"{author}/{repository_name} - v{current_version}", fg="magenta")
    )
    yield from processor(click.style(description, fg="magenta"))

    if check_for_updates:

        branch, version_file = VERSION_FILE_PATH
        upstream_version = VERSION_REGEX.search(
            session.get(
                f"https://raw.githubusercontent.com/{author}/{repository_name}/{branch}/{version_file}"
            ).text
        ).group(1)

        if tuple(upstream_version.split(".")) > tuple(current_version.split(".")):
            yield from processor(
                click.style(f"Update available: {upstream_version}", fg="yellow")
            )


def banner_gift_wrapper(session, current_version, *, check_for_updates=False):
    def wrapper(f):
        def __inner__(*args, log_level, log_file, **kwargs):

            if log_level < 20:
                return f(*args, log_level=log_level, log_file=log_file, **kwargs)

            for _ in iter_banner(
                session,
                current_version,
                check_for_updates=check_for_updates,
            ):
                click.echo(_)

            return f(*args, log_level=log_level, log_file=log_file, **kwargs)

        return __inner__

    return wrapper
