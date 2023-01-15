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

        if not components:
            return fallback

        if len(components) == 1:
            return components[0]

        processed_components = list(
            stdout_processor(component) if stdout_processor is not None else component
            for component in components
        )

        enumerated_components = tuple(enumerate(processed_components, 1))

        for n, cout in reversed(enumerated_components):
            if not isinstance(cout, str):
                raise TypeError(
                    "The stdout_processor must return a string and not {!r}.".format(
                        type(cout)
                    )
                )
            console.print(Text(f"{n}.", style="b blue"), cout)

        choices = list(map(str, range(1, len(enumerated_components) + 1)))

        choice = Prompt.ask(
            Text(
                f"Select the {component_name} (automatically selects the top {component_name}) ",
                style="dim",
            )
            + Text(f'[{"/".join(choices)}]', style="b blue"),
            default=1,
            console=console,
            choices=choices,
            show_choices=False,
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


def quality_prompt(console, streams, *, force_selection_string=None):

    if len(streams) == 1:
        return streams[0]

    if force_selection_string is not None:
        return quality_prompt(console, filter_quality(streams, force_selection_string))

    def stream_stdout_processor(content: dict):
        parsed_url = yarl.URL(content["stream_url"])

        title = content.get("title")

        if title is None:
            title = f"{parsed_url.name} // {parsed_url.host!r}"

        if content.get("subtitle"):
            title += " (with subtitles)"

        quality = content.get("quality")

        if quality is not None:
            title += f" [{quality}p]"
        else:
            extension = parsed_url.suffix.lstrip(".")

            if extension in ("m3u8", "mpd", "m3u"):
                title += f" [Adaptive quality: {extension}]"
            else:
                title += f" [Unknown quality: {extension}]"

        return title

    value = get_prompt_manager()(
        console,
        streams,
        stdout_processor=stream_stdout_processor,
        component_name="stream",
    )

    return value
