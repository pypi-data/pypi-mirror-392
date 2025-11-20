import logging
import signal
import threading
from typing import Protocol

import pebble

#
# Clean up pebble process pool on signals
#


class PostPebblePoolCleanup(Protocol):
    def __call__(self, forced_shutdown: bool = False) -> None: ...


def _pebble_cleanup_pool(
    force_shutdown: bool = False,
    pool: pebble.ProcessPool = None,
    futures: list[pebble.ProcessFuture] = None,
    post_cleanup: PostPebblePoolCleanup = None,
    logger: logging.Logger = None,
):
    if futures is None:
        futures = []
    # Cancel remaining tasks
    logger.debug("Cancelling tasks pool ...")
    for future in futures:
        if not future.done():
            future.cancel()

    if force_shutdown:
        # Stop current/pending tasks
        logger.debug("Forcing stop pool...")
        pool.stop()
    else:
        # Stop once all current/pending tasks have completed
        logger.debug("Closing worker pool...")
        pool.close()
        logger.debug("Waiting for pool workers to all be shutdown...")
        if threading.current_thread() == threading.main_thread():
            pool.join()

    if post_cleanup is not None:
        post_cleanup(force_shutdown=force_shutdown)


def pebble_cleanup_pool(
    logger=None,
    pool: pebble.ProcessPool = None,
    futures: list[pebble.ProcessFuture] = None,
    post_cleanup: PostPebblePoolCleanup = None,
):
    if futures is None:
        futures = []
    _pebble_cleanup_pool(
        force_shutdown=False, logger=logger, pool=pool, futures=futures, post_cleanup=post_cleanup
    )


def pebble_cleanup_pool_on_signal(
    force_shutdown: bool = False,
    logger=None,
    pool: pebble.ProcessPool = None,
    futures: list[pebble.ProcessFuture] = None,
    signals: dict[int, str] = None,
    post_cleanup: PostPebblePoolCleanup = None,
):
    """Clean up pebble process pool on signals

    :param force_shutdown: bool:  (Default value = False)
    :param logger:  (Default value = None)
    :param pool: pebble.ProcessPool:  (Default value = None)
    :param futures: List[pebble.ProcessFuture]:  (Default value = [])
    :param signals: Dict[int:
    :param str]:  (Default value = {signal.SIGINT: "SIGINT")
    :param signal.SIGTERM: "SIGTERM"}:
    :param post_cleanup: PostPebblePoolCleanup:  (Default value = None)

    """
    if futures is None:
        futures = []
    signals = signals or {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM"}

    def _handler(_signum, _frame):
        # logger.critical(f"Received {signals.get(signum, signum)} signal ...")
        _pebble_cleanup_pool(
            force_shutdown=force_shutdown,
            logger=logger,
            pool=pool,
            futures=futures,
            post_cleanup=post_cleanup,
        )

    # Register signals handlers
    for s in signals:
        signal.signal(s, _handler)
