import logging.handlers
import queue


class StreamlitLogHandler(logging.Handler):
    def __init__(self, q: queue.Queue):
        super().__init__()
        self.q = q
        self.formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="[%m/%d/%Y %X]"
        )

    def emit(self, record):
        msg = self.format(record)
        self.q.put(msg)
