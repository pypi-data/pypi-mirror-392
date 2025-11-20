import logging
import signal

from pyexpect import expect

from constellate.logger.handler.stringhandler import StringHandler
from constellate.runtime.stackframe.sampler import sample_stackframe_on_signal


def test_stackframe_on_signal() -> None:
    handler = StringHandler(capacity=0)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Register signal handler
    sig = signal.SIGUSR2
    sample_stackframe_on_signal(signum=sig.value, logger=logger)

    # Send signal
    signal.raise_signal(sig)

    expect(handler.output()).to_contain("Current thread")
