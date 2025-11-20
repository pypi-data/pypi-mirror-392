import logging
import signal
from enum import Enum, auto
from typing import Union
from collections.abc import Callable

Signal = int
SignalHandler = Union[Callable[[int, object], None], None, type(signal.SIG_IGN)]


class SignalHandlerOverride(Enum):
    OVERRIDE_ALWAYS = auto()
    OVERRIDE_WRAP = auto()


def register_signal_handler(
    signum: Signal = signal.SIGUSR2,
    handler: SignalHandler = None,
    logger: logging.Logger = None,
    mode: SignalHandlerOverride = SignalHandlerOverride.OVERRIDE_WRAP,
) -> None:
    old_handler = signal.getsignal(signum)

    def _wrapper_handler(signum2, _frame):
        sig = signal.Signals(signum2)
        logger.debug(f"Signal {sig.name} received.")

        if handler is not None:
            handler(signum2, _frame)

        if mode == SignalHandlerOverride.OVERRIDE_ALWAYS:
            return
        if mode == SignalHandlerOverride.OVERRIDE_WRAP:
            if old_handler is None:
                # Signal handler not installed by python
                logger.debug(f"{sig}: wrapped default signal handler was not installed by Python")
            elif old_handler == signal.SIG_IGN:
                # Ignore the given signal. Hence, no handler to be called
                logger.debug(f"{sig}: wrapped default signal handler is a NOP")
            elif old_handler == signal.SIG_DFL:
                # Run default function for the signal
                logger.debug(f"{sig}: wrapped default handler cannot be executed within python")
            elif callable(old_handler):
                old_handler(signum2, _frame)
            else:
                logger.fatal(f"{sig}: wrapped default handler not executed due to programmer error")

    # Register new handler for signal
    signal.signal(signum, _wrapper_handler)

    sig = signal.Signals(signum).name if signum is not None else signum
    logger.debug(f"{sig}: new handler registered")
