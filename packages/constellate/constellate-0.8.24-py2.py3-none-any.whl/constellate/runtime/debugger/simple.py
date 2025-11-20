import logging
import signal

from constellate.package.package import package_available
from constellate.runtime.debugger.config import DebuggerConfig, Endpoint
from constellate.runtime.debugger.protocol import DebuggerProtocol

if package_available("pydevd_pycharm"):
    from constellate.runtime.debugger.pycharm.debugger import run_debugger as run_debugger_pycharm
else:

    def run_debugger_pycharm(**kwargs):
        raise ImportError()


if package_available("debugpy"):
    from constellate.runtime.debugger.vscode.debugger import run_debugger as run_debugger_vscode
else:

    def run_debugger_vscode(**kwargs):
        raise ImportError()


from constellate.runtime.signal.helper import (
    register_signal_handler,
    Signal,
    SignalHandler,
    SignalHandlerOverride,
)
from constellate.virtualization.common.common import is_containerized


def run_debugger(
    logger: logging.Logger = None,
    config: DebuggerConfig = None,
) -> None:
    try:
        if config.protocol in [DebuggerProtocol.VSCODE]:
            config.endpoints = (config.endpoints if config.endpoints is not None else []) + [
                Endpoint("localhost", 5678)
            ]
            run_debugger_vscode(config=config, logger=logger)
        elif config.protocol in [DebuggerProtocol.DEFAULT, DebuggerProtocol.PYCHARM]:
            config.endpoints = (config.endpoints if config.endpoints is not None else []) + [
                # Local machine: client app runs in Docker => containerized
                # Local machine: client app runs without docker => not containerized
                Endpoint("host.docker.internal", 4444)
                if is_containerized()
                else Endpoint("localhost", 4444)
            ]
            run_debugger_pycharm(config=config, logger=logger)
    except ImportError:
        logger.error("Cannot run debugger", exc_info=1)


def run_debugger_on_condition(
    config: DebuggerConfig = None,
    condition: bool = False,
    logger: logging.Logger = None,
) -> None:
    if condition:
        run_debugger(config=config, logger=logger)


def run_debugger_on_stage(
    config: DebuggerConfig = None,
    stage: str = None,
    enabled_stages: list[str] = None,
    logger: logging.Logger = None,
) -> None:
    """Enable remote debugger if the current stage is one of the enabled stages"""
    stages = enabled_stages if enabled_stages is not None else []
    run_debugger_on_condition(config=config, condition=stage in stages, logger=logger)


def run_debugger_on_signal(
    signum: Signal = signal.SIGUSR2,
    handler: SignalHandler = None,
    logger: logging.Logger = None,
    config: DebuggerConfig = None,
    mode: SignalHandlerOverride = SignalHandlerOverride.OVERRIDE_ALWAYS,
) -> None:
    new_handler = None
    if handler is not None:
        new_handler = handler
    else:

        def _handler(_signum2, _frame):
            run_debugger(config=config, logger=logger)

        new_handler = _handler

    register_signal_handler(signum=signum, handler=new_handler, logger=logger, mode=mode)
