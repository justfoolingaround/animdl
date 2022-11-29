from .base_player import BasePlayer


class FFPlay(BasePlayer):

    opts_spec = {
        "headers": "-headers",
        "metadata": "-metadata",
        "title_field": "title",
    }

    def play(self, stream_url, headers=None, title=None, opts=None, **kwargs):
        args = (self.executable, stream_url)

        if opts is not None:
            args += tuple(opts)

        if headers is not None:
            args += (
                f"{self.opts_spec['headers']}={self.headers_joiner.join(f'{key}: {value}' for key, value in headers.items())}",
            )

        if title is not None:
            args += (self.opts_spec["metadata"], f"{self.opts_spec['title']}={title}")

        self.spawn(args)
