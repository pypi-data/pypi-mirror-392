import functools

import pebble
import pytest
from pyexpect import expect

import constellate.constant.concurrency
from constellate.concurrency.simple.simple import thread, process


def test_logical_cpu_count() -> None:
    expect(constellate.constant.concurrency.LOGICAL_CPUS_COUNT > 0).to_be(True)


@pytest.mark.asyncio
@pytest.mark.parametrize("pool", [None, pebble.ThreadPool()])
async def test_concurrency_simple_thread(pool) -> None:
    @thread(pool=pool)
    def _compute(*args, **kwargs):
        return sum(list(args)) + sum(kwargs.values())

    expect(await _compute(1, 1, b=1, c=1)).to_be(4)


def __compute_via_process(**kwargs):
    return sum(kwargs.values())


@pytest.mark.asyncio
@pytest.mark.parametrize("pool", [None, pebble.ProcessPool()])
async def test_concurrency_simple_process(pool) -> None:
    compute = functools.partial(process, __compute_via_process, pool=pool)
    expect(await compute(b=1, c=1)).to_be(2)
