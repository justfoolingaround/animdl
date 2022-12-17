from sys import platform
from tempfile import NamedTemporaryFile

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
        self,
        stream_url,
        subtitles=None,
        headers=None,
        title=None,
        opts=None,
        chapters=None,
        **kwargs,
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

        if chapters:

            # NOTE: This could be achieved with a PIPE.
            # This is not done in this case because you
            # only PIPE one argument at a time, and this
            # is expected to be limiting in the future.
            # PIPE-ing whole media is more suitable.

            with NamedTemporaryFile("w", delete=False) as chapters_file:
                chapters_file.write(";FFMETADATA1")

                for chapter in chapters:
                    chapters_file.write(
                        f"""
[CHAPTER]
TIMEBASE=1/1000
START={int(chapter["start"] * 1000)}
END={int(chapter["end"] * 1000)}
TITLE={chapter["chapter"]}"""
                    )

                chapters_file.write("\n")
            args += (f"--chapters-file={chapters_file.name}",)

        args += tuple(self.optimisation_args)

        self.spawn(args)


class CelluloidPlayer(MPVDefaultPlayer):
    optimisation_args = [
        "--new-window",
    ]

    def __new__(cls, *args, **kwargs):

        for key, value in cls.opts_spec.items():
            cls.opts_spec[key] = f"--mpv-{value.lstrip('-')}"

        return cls


IINAPlayer = CelluloidPlayer
