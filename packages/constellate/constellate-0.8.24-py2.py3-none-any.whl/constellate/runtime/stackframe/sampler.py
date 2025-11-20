import faulthandler
import logging
import os
import signal
import tempfile

from constellate.runtime.signal.helper import (
    register_signal_handler,
    Signal,
    SignalHandler,
    SignalHandlerOverride,
)


def sample_stackframe_on_signal(
    signum: Signal = signal.SIGUSR2,
    handler: SignalHandler = None,
    logger: logging.Logger = None,
    mode: SignalHandlerOverride = SignalHandlerOverride.OVERRIDE_ALWAYS,
) -> None:
    new_handler = None
    if handler is not None:
        new_handler = handler
    else:

        def _handler(_signum2, _frame):
            with tempfile.TemporaryFile() as f:
                stack = _sample_stackframe(f)
                logger.debug(f"Stack frame data:\n{stack}")
                logger.debug(
                    f"Alternatively invoke for more details: austin (or austin-ui) --pid={os.getpid()} --children --where={os.getpid()}"
                )

        new_handler = _handler

    register_signal_handler(signum=signum, handler=new_handler, logger=logger, mode=mode)


def _sample_stackframe(file) -> str:
    faulthandler.dump_traceback(file=file, all_threads=True)
    file.seek(0)

    def _decode(line: bytes) -> str:
        return line.decode("utf-8")

    return "".join(map(_decode, file.readlines()))
