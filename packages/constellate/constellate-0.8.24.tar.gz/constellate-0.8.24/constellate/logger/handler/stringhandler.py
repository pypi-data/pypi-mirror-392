import logging
from io import StringIO
from logging import StreamHandler
from logging.handlers import MemoryHandler


class StringHandler(MemoryHandler):
    def __init__(self, capacity):
        logging.handlers.MemoryHandler.__init__(self, capacity, flushLevel=logging.CRITICAL + 1)
        self.stream_buffer = StringIO()
        self.handler = StreamHandler(stream=self.stream_buffer)
        self.setTarget(self.handler)

    def shouldFlush(self, record):
        return False

    def output(self):
        self.flush()
        return self.stream_buffer.getvalue()
