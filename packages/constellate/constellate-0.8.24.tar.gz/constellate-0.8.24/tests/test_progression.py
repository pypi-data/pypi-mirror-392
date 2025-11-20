import logging
from io import StringIO

import pytest
from pyexpect import expect

from constellate.progression.progres import Progress

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
@pytest.mark.parametrize("fn_logger", [None, log.warning])
async def test_progress_logged(fn_logger) -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream=stream)
    handler.setLevel(logging.DEBUG)

    try:
        log.addHandler(handler)

        progress = Progress(log=fn_logger)

        values = [1, 2]
        values2 = []
        async for i in progress(iterator=values):
            values2.append(i)

        expect(set(values2)).to_equal(set(values))
        if fn_logger is not None:
            expect(stream.getvalue()).to_contain("it/s")
    finally:
        log.removeHandler(handler)
