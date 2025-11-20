import logging
import os

import debugpy

from constellate.runtime.debugger.config import DebuggerConfig


def run_debugger(config: DebuggerConfig = None, logger: logging.Logger = None) -> None:
    for endpoint in config.endpoints:
        try:
            logger.debug(f"Debugger client will try to connect to {endpoint.host}:{endpoint.port}")
            logger.debug(
                f"To connect application PID {os.getpid()} at {endpoint.host}:{endpoint.port}'"
            )
            debugpy.listen((endpoint.host, endpoint.port))
            if config.wait:
                debugpy.wait_for_client()
            logger.debug("Connected to debugger")
            break
        except BaseException:
            logger.error("Cannot wait for debugger client", exc_info=1)
