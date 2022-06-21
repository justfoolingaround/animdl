import subprocess
import sys
from collections import defaultdict

import click
import yarl

from ...config import FZF_EXECUTABLE, FZF_OPTS, FZF_STATE
from .intelliq import filter_quality


def default_prompt(
    logger,
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

    if not components:
        if error_message is not None:
            logger.critical(error_message)
        return fallback

    for component_id, component in enumerate(components, 1):
        out = stdout_processor(component) if stdout_processor else component

        if escape_output:
            out = repr(out)[1:-1]

        logger.info("{:02d}: {}".format(component_id, out))

    if len(component) == 1:
        logger.debug(
            "The prompt list has only one {}. Returning it.".format(component_name)
        )
        return components[0]

    user_selection = (
        click.prompt(
            "Select the {} using index".format(component_name),
            default=1,
            type=int,
            show_default=True,
        )
        - 1
    )

    return components[user_selection % len(components)]


def fzf_prompt(
    logger,
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
            logger.critical(error_message)
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
