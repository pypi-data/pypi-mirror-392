import logging
import sys

from constellate.runtime.debugger.config import DebuggerConfig


def setup_debugger(
    host: str = "host.docker.internal",
    port: int = 4444,
    logger: logging.Logger = None,
):
    try:
        sys.path.append("pydevd-pycharm.egg")
        import pydevd_pycharm
    except BaseException:
        logger.error(
            "ERROR: PyCharm's remote debugging library not installed: "
            " - pydevd-pycharm~=XXX.XXXX.XX; sys.platform=='linux'",
            exc_info=1,
        )
        raise

    pydevd_pycharm.settrace(
        host, port=port, stdout_to_server=True, stderr_to_server=True, suspend=False
    )


def run_debugger(config: DebuggerConfig = None, logger: logging.Logger = None) -> None:
    for endpoint in config.endpoints:
        logger.debug(f"Connecting to debugger server {endpoint.host}:{endpoint.port}")
        if config.wait:
            try:
                setup_debugger(host=endpoint.host, port=endpoint.port, logger=logger)
            except BaseException:
                logger.error("Failed to connect debugger server", exc_info=1)
        logger.debug("Connected to debugger")
