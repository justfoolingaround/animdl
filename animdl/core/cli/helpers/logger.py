import logging

import click


class ColouredFormatter(logging.Formatter):

    logging_colours = {
        "WARNING": "yellow",
        "INFO": "green",
        "DEBUG": "blue",
        "CRITICAL": "red",
        "ERROR": "red",
    }

    def format(self, record: logging.LogRecord) -> str:

        foreground = self.logging_colours.get(record.levelname, "white")

        record.levelname = click.style(record.levelname, fg=foreground)
        record.name = click.style(record.name, fg=foreground)

        return super().format(record)


class FileLoggingFormatter(logging.Formatter):

    logging_format = (
        "[%(filename)s:%(lineno)d - %(asctime)s - %(name)s: %(levelname)s] %(message)s"
    )

    def __init__(self):
        super().__init__(fmt=self.logging_format)


def setup_loggers(
    logging_format=f"[{click.style('%(filename)s:%(lineno)d', fg='magenta')} - %(asctime)s - %(name)s: %(levelname)s] %(message)s",
    file_logging_format=f"[%(filename)s:%(lineno)d - %(asctime)s - %(name)s: %(levelname)s] %(message)s",
):
    def wrapper(f):
        def __inner__(*args, log_level=20, log_file=None, **kwargs):

            basic_config_kwargs = {
                "format": logging_format,
                "level": log_level,
            }

            if log_file is not None:
                basic_config_kwargs.update(
                    filename=log_file,
                    filemode="a",
                )

            logging.basicConfig(**basic_config_kwargs)

            class SmartColouredLogger(logging.Logger):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                    self.propagate = False

                    if log_file is not None:
                        file_stream_handler = logging.FileHandler(
                            log_file, "a", encoding="utf-8"
                        )
                        file_stream_handler.setFormatter(
                            logging.Formatter(fmt=file_logging_format)
                        )
                        self.addHandler(file_stream_handler)
                    else:
                        stream_handler = logging.StreamHandler()
                        stream_handler.setFormatter(
                            ColouredFormatter(fmt=logging_format)
                        )
                        self.addHandler(stream_handler)

            logging.setLoggerClass(SmartColouredLogger)

            return f(*args, **kwargs, log_file=log_file, log_level=log_level)

        return __inner__

    return wrapper
