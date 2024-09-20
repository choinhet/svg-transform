import logging.handlers
import queue


class StreamlitLogHandler(logging.Handler):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.q = q
        self.formatter = logging.Formatter(
            fmt="%(asctime)s\t%(levelname)s %(message)s",
            datefmt="[%m/%d/%Y %X]"
        )
        self.setFormatter(self.formatter)
        self.setLevel(logging.INFO)

    def emit(self, record):
        msg = self.format(record)
        self.q.put(msg)
