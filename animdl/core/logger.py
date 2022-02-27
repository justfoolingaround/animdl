import logging

COLORS = {
    "WARNING": "\x1b[33m",
    "INFO": "\x1b[32m",
    "DEBUG": "\x1b[36m",
    "CRITICAL": "\x1b[91m",
    "ERROR": "\x1b[31m",
}


class LoggingFormatter(logging.Formatter):

    use_color = True
    logging_format = "[\x1b[35m%(filename)s:%(lineno)d\x1b[39m - %(asctime)s - %(name)s: %(levelname)s] %(message)s"

    def __init__(self):
        super().__init__(fmt=self.logging_format)

    def format(self, record: logging.LogRecord) -> str:

        if self.use_color:
            color = COLORS.get(record.levelname)
            record.levelname = "{}{}\x1b[39m".format(color, record.levelname[0])
            if record.name:
                record.name = "{}{}\x1b[39m".format(color, record.name)

        return super().format(record)


class FileLoggingFormatter(logging.Formatter):

    logging_format = "[%(filename)s:%(lineno)d\x1b - %(asctime)s - %(name)s: %(levelname)s] %(message)s"

    def __init__(self):
        super().__init__(fmt=self.logging_format)


class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.propagate = False

        formatter = LoggingFormatter()

        if self.FILE_STREAM is not None:
            file_stream_handler = logging.FileHandler(
                self.FILE_STREAM, "a", encoding="utf-8"
            )
            file_stream_handler.setFormatter(FileLoggingFormatter())
            self.addHandler(file_stream_handler)
        else:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.addHandler(stream_handler)


def configure_logger(logger_class=Logger):
    logging.setLoggerClass(logger_class)
