from warnings import warn

from .base_player import BasePlayer


class AndroidIntentVIEW(BasePlayer):

    intent = "android.intent.action.VIEW"

    warnable_opts = {"headers", "subtitles"}

    def play(self, stream_url, **kwargs):

        args = (
            "am",
            "start",
            "-a",
            self.intent,
            "-d",
            stream_url,
        )

        keys = set(kwargs.keys())

        if self.warnable_opts & keys:
            warn(
                f"Android does not support {', '.join(map(repr, self.warnable_opts & keys))} options. "
                "These options may cause the stream to fail to load or one or more stream attributes to fail."
            )

        self.spawn(args)
