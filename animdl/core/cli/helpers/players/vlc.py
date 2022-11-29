from warnings import warn

from .base_player import BasePlayer


class VLCPlayer(BasePlayer):

    optimisation_args = ("--http-forward-cookies",)

    opts_spec = {
        "http_referrer": "--http-referrer",
        "user_agent": "--user-agent",
        "subtitle": "--sub-file",
    }

    def play(
        self, stream_url, subtitles=None, headers=None, title=None, opts=None, **kwargs
    ):
        args = (self.executable, stream_url)

        if opts is not None:
            args += tuple(opts)

        if headers is not None:
            lowercased_headers = {key.lower(): value for key, value in headers.items()}

            keys = set(lowercased_headers.keys())

            if "user-agent" in keys:
                args += (
                    f"{self.opts_spec['user_agent']}={lowercased_headers['user-agent']}",
                )

            if "referer" in keys:
                args += (
                    f"{self.opts_spec['http_referrer']}={lowercased_headers['referer']}",
                )

            extra = keys - {"user-agent", "referer"}

            if extra:
                warn(
                    f"VLC does not support {', '.join(map(repr, extra))} headers. "
                    "This may result in stream loading failure."
                )

        if title is not None:
            args += (f"--meta-title={title}",)

        if subtitles is not None:
            args += tuple(f"--sub-file={subtitles}" for subtitles in subtitles)

        self.spawn(args)
