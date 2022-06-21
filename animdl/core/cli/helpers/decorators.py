import click
from anchor.strings.parsing.ranges import iter_conditions

from .banner import banner_gift_wrapper
from .logger import setup_loggers
from .player import PLAYER_MAPPING

accept_all = lambda *args, **kwargs: True


class RangeParameter(click.ParamType):

    name = "rangetype"

    def convert(self, value, param, ctx):

        if value is None:
            return None

        conditions = list(iter_conditions(value))

        if not conditions:
            return lambda *args, **kwargs: True

        return lambda *args, **kwargs: any(
            condition(*args, **kwargs) for condition in conditions
        )


def options_stack(options=[]):
    def __inner__(func):
        for option in options:
            func = option(func)

        return func

    return __inner__


def logging_options(
    log_file_args=("--log-file",),
    log_level_args=("--log-level", "-ll"),
):

    return options_stack(
        [
            click.option(
                *log_file_args,
                help="Set a log file to log everything to.",
                required=False,
            ),
            click.option(
                *log_level_args,
                help="Set the integer log level.",
                type=int,
                default=20,
            ),
        ]
    )


def content_fetch_options(
    query_argument_name="query",
    range_args=("-r", "--range"),
    *,
    include_quality_options=True,
    quality_args=("-q", "--quality"),
    include_special_options=True,
    special_args=("-s", "--special"),
    default_quality_string=None,
):

    options = [
        click.argument(
            query_argument_name,
            required=True,
        ),
        click.option(
            *range_args,
            help="Select ranges of anime.",
            required=False,
            default=":",
            type=RangeParameter(),
        ),
    ]

    if include_special_options:
        options.append(
            click.option(
                *special_args,
                help="Special range selection.",
                required=False,
                default="",
                type=str,
            ),
        )

    if include_quality_options:
        options.append(
            click.option(
                *quality_args,
                help="Use quality strings.",
                required=False,
                default=default_quality_string,
            )
        )

    return options_stack(options)


def automatic_selection_options(
    index_args=("--index",),
):

    return options_stack(
        [
            click.option(
                *index_args,
                required=False,
                default=None,
                show_default=False,
                type=int,
                help="Index for the auto flag.",
            ),
        ]
    )


def download_options(
    download_dir_args=("-d", "--download-dir"),
    idm_args=("--idm",),
    default_download_dir=None,
):

    return options_stack(
        [
            click.option(
                *download_dir_args,
                help="Download directory for downloads.",
                required=False,
                default=default_download_dir,
                show_default=False,
                type=click.Path(exists=True, file_okay=False, dir_okay=True),
            ),
            click.option(
                *idm_args,
                is_flag=True,
                default=False,
                help="Download anime using Internet Download Manager",
            ),
        ]
    )


def player_options(
    player_opts_args=("--player-opts",),
    player_args=("-p", "--player"),
    default_player=None,
):

    return options_stack(
        [
            click.option(
                *player_opts_args,
                help="Arguments that are to be passed to the player call.",
                required=False,
            ),
            click.option(
                *player_args,
                help="Select which player to play from.",
                required=False,
                default=default_player,
                show_default=True,
                show_choices=True,
                type=click.Choice(PLAYER_MAPPING.keys(), case_sensitive=False),
            ),
        ]
    )
