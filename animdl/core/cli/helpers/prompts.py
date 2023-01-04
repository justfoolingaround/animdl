import subprocess
import sys
from collections import defaultdict

import click
import yarl
from rich.prompt import Prompt
from rich.text import Text

from ...config import FZF_EXECUTABLE, FZF_OPTS, FZF_STATE
from .intelliq import filter_quality
from .stream_handlers import context_raiser


def default_prompt(
    console,
    components,
    *,
    processor=None,
    component_name="result",
    fallback=None,
    error_message=None,
    stdout_processor=None,
    escape_output=False,
):

    with context_raiser(
        console, f"[b]Waiting for you to select a {component_name!r}.[/]"
    ):
        if processor is None:
            components = list(components)
        else:
            components = list(processor(component) for component in components)

        if len(components) == 1:
            return components[0]

        processed_components = list(
            stdout_processor(component) if stdout_processor is not None else component
            for component in components
        )

        for n, cout in enumerate(processed_components, 1):
            if not isinstance(cout, str):
                raise TypeError(
                    "The stdout_processor must return a string and not {!r}.".format(
                        type(cout)
                    )
                )
            console.print(f"[bold blue]{n}[/bold blue].", Text(cout, style="u b red"))

        choice = Prompt.ask(
            Text(
                f"Select the {component_name} (automatically selects the top {component_name})",
                style="dim",
            ),
            default=1,
            console=console,
            choices=list(map(str, range(1, n + 1))),
            show_choices=True,
        )

    return components[int(choice) - 1]


def fzf_prompt(
    console,
    components,
    *,
    processor=None,
    component_name="result",
    fallback=None,
    error_message=None,
    stdout_processor=None,
    escape_output=False,
):
    if processor is None:
        components = list(components)
    else:
        components = list(processor(component) for component in components)

    if len(components) == 1:
        return components[0]

    stdout_mapout = {}

    for component_output, component in zip(
        (stdout_processor(component) for component in components)
        if stdout_processor
        else components,
        components,
    ):

        if not isinstance(component_output, str):
            raise TypeError(
                "The stdout_processor must return a string and not {!r}.".format(
                    type(component_output)
                )
            )

        if escape_output:
            component_output = repr(component_output)[1:-1]

        if component_output in stdout_mapout:
            component_output += " (apparent duplicate {})".format(component_name)

        stdout_mapout[component_output] = component

    if not stdout_mapout:
        if error_message is not None:
            console.print(error_message, style="bold red")
        return fallback

    fzf_args = [
        FZF_EXECUTABLE,
        "--header={}".format(
            f"Select the {component_name} (automatically selects the top {component_name})"
        ),
    ] + FZF_OPTS

    process = subprocess.Popen(
        fzf_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    selection, _ = process.communicate(b"\n".join(map(str.encode, stdout_mapout)))

    if process.returncode in [1, 130]:
        return components[0]

    return stdout_mapout[selection.decode()[:-1]]


def get_prompt_manager(*, fallback=default_prompt):

    if not sys.stdout.isatty():
        return fallback

    if FZF_STATE:
        return fzf_prompt

    return fallback


def quality_prompt(logger, log_level, streams, *, force_selection_string=None):

    if len(streams) == 1:
        return streams[0]

    if force_selection_string is not None:
        return quality_prompt(
            logger, log_level, filter_quality(streams, force_selection_string)
        )

    component_dictionary = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for count, anime in enumerate(streams, 1):
        stream_title = click.style(anime.get("title", "Uncategorised"), fg="cyan")
        stream_quality = click.style(
            anime.get("quality", "Anonymous quality"), fg="magenta"
        )

        substate = click.style(
            (
                "Hard Subtitles",
                "Soft Subtitles",
            )[bool(anime.get("subtitle", []))],
            fg="yellow",
        )

        parsed_stream_url = "{0.name} / {0.host}".format(
            yarl.URL(anime.get("stream_url"))
        )

        component_dictionary[stream_title][stream_quality][substate].append(
            f"{count:02d} / {parsed_stream_url}"
        )

    for category, qualities in component_dictionary.items():
        logger.info(category)
        for quality, subtitles in qualities.items():
            logger.info(quality)
            for subtitle, animes in subtitles.items():
                logger.info(subtitle)
                for anime in animes:
                    logger.info(anime)

    return streams[
        (
            ask(
                log_level,
                text="Select above, using the stream index",
                show_default=True,
                default=1,
                type=int,
            )
            - 1
        )
        % len(streams)
    ]


def ask(log_level, **prompt_kwargs):

    if log_level > 20:
        return prompt_kwargs.get("default")

    return click.prompt(**prompt_kwargs)
