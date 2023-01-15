"""
BasePlayer, (c) 2022-present, animdl authors

Note from developer, KR:

This is the base class for all players. All players
**must** inherit from this class.

    class YourPlayer(BasePlayer):
        ...

The .play() method should not necessarily call .spawn().

If you can handle multiple streams with a single process,
that is suggested.

Your class must make use of .opts_spec to map options with
their corresponding arguments. This is done so that the
class may be re-used when writing similar player wrappers.

Your class must have a .optimisation_args attribute. May it
be an empty tuple. This is done so that any developer may
add forced arguments to the player for project-specific
optimisations.

Do not make .play() delay the execution of the player or wait
for the process to complete. You must make use of .process
attribute to do so.

.spawn() kills pre-existing processes. Do not change this behaviour.

.indicate_error() is a method that is called when a player
process has been deemed offline. If an error occured in the player,
during playback, override this method to indicate the error.

This feature is to make handling errors from the player easier
irrespective of the player persistence.

Lastly,

This is not made for any specific project. These players are made
so that they can be used in any project. Hence, do not make
anything with project-specific code.
"""

import subprocess


class BasePlayer:

    opts_spec: dict
    optimisation_args: tuple

    def __init__(self, executable, args=()):
        self.executable = executable
        self.args = args

        self.process: subprocess.Popen = None

    def play(self):
        raise NotImplementedError

    def spawn(self, *args, **kwargs):
        if self.process is not None:
            self.process.kill()

        self.process = subprocess.Popen(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process is not None:
            self.process.wait()

    def indicate_error(self):
        return self.process.returncode
