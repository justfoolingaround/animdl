from sys import platform

from .base_player import BasePlayer


class MPVDefaultPlayer(BasePlayer):

    optimisation_args = [
        "--force-window=immediate",
    ]
    headers_joiner = "\r\n"

    if platform == "win32":
        path_joiner = ";"
    else:
        path_joiner = ":"

    opts_spec = {
        "headers": "--http-header-fields",
        "title": "--title",
        "subtitles": "--sub-files",
        "media-title": "--force-media-title",
    }

    def play(
        self, stream_url, subtitles=None, headers=None, title=None, opts=None, **kwargs
    ):

        args = (self.executable, stream_url)

        if opts is not None:
            args += tuple(opts)

        if headers is not None:
            args += (
                f"{self.opts_spec['headers']}={self.headers_joiner.join(f'{key}: {value}' for key, value in headers.items())}",
            )

        if title is not None:
            args += (
                f"{self.opts_spec['title']}={title}",
                f"{self.opts_spec['media-title']}={title}",
            )

        if subtitles is not None:
            args += (
                f"{self.opts_spec['subtitles']}={self.path_joiner.join(subtitles)}",
            )

        args += tuple(self.optimisation_args)

        self.spawn(args)


class CelluloidPlayer(MPVDefaultPlayer):
    optimisation_args = [
        "--new-window",
    ]

    def __new__(cls, *args, **kwargs):

        for key, value in cls.opts_spec.items():
            cls.opts_spec[key] = f"--mpv-{value.lstrip('-')}"

        return super().__new__(cls, *args, **kwargs)


IINAPlayer = CelluloidPlayer
