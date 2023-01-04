import datetime
import functools

from rich.console import Console
from rich.style import Style
from rich.text import Text


@functools.lru_cache()
def get_console():
    return Console(stderr=True, color_system="auto")


class ContextRaiser:
    def __init__(self, console, message=None, *, indent_string=" " * 2, name="unknown"):
        self.indent_string = indent_string
        self.console = console
        self.default_writer = console.print
        self.message = message

        self.ctx_name = name

    def __enter__(self):
        if self.message:
            self.console.print(self.message)

        def print(*args, **kwargs):
            self.default_writer(self.indent_string, *args, **kwargs)

        self.console.print = print

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type:
            if isinstance(exc_value, (KeyboardInterrupt, SystemExit)):
                self.console.print(
                    f"Exiting from the {self.ctx_name} context.",
                    style="bold red",
                )

        self.console.print = self.default_writer


context_raiser = ContextRaiser


def is_day(date, month, day):
    return date.month == month and date.day == day


custom_greetings = {
    lambda date: is_day(date, 1, 1): Text("Happy new year! 🎉", style="bold yellow"),
    lambda date: is_day(date, 12, 25): Text("Merry Christmas! 🎄", style="bold cyan"),
    lambda date: is_day(date, 4, 1): Text(
        "Happy April Fools' Day! 🎉", style="bold green"
    ),
    lambda date: is_day(date, 10, 31): Text(
        "Ooh, spooky! Happy Halloween. 🎃", style="yellow"
    ),
    lambda date: is_day(date, 3, 14): Text("Happy Valentine's Day ❤!", style="red"),
}


def iter_greetings():

    datetime_now = datetime.datetime.now()

    for condition, message in custom_greetings.items():
        if condition(datetime_now):
            yield message

    yield datetime_now.strftime("It is %I:%M %p on a [bold red]beautiful[/] %A!")
