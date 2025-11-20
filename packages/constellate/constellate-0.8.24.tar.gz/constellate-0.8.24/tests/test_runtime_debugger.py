import logging
import signal

import pytest
from pyexpect import expect

from constellate.logger.handler.stringhandler import StringHandler
from constellate.runtime.debugger.config import DebuggerConfig
from constellate.runtime.debugger.protocol import DebuggerProtocol
from constellate.runtime.debugger.simple import run_debugger_on_signal
from constellate.runtime.signal.helper import SignalHandlerOverride


@pytest.mark.parametrize("protocol", list(DebuggerProtocol))
def test_debugger_on_signal(protocol) -> None:
    handler = StringHandler(capacity=0)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    sig = signal.SIGUSR2

    # Register signal handler
    if protocol in [DebuggerProtocol.VSCODE]:
        run_debugger_on_signal(
            signum=sig.value,
            logger=logger,
            config=DebuggerConfig(protocol=protocol, wait=False),
            mode=SignalHandlerOverride.OVERRIDE_ALWAYS,
        )
    elif protocol in [DebuggerProtocol.PYCHARM, DebuggerProtocol.DEFAULT]:
        run_debugger_on_signal(
            signum=sig.value,
            logger=logger,
            config=DebuggerConfig(protocol=protocol, wait=False),
            mode=SignalHandlerOverride.OVERRIDE_ALWAYS,
        )

    # Send signal
    signal.raise_signal(sig)

    text = handler.output()
    if protocol in [DebuggerProtocol.VSCODE]:
        pass
    else:
        expect(text).to_contain("Connected to debugger")
