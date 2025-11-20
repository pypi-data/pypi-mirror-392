from typing import Any
from collections.abc import Callable
from collections.abc import Generator

from decorator import decorator
from numba_progress import ProgressBar


@decorator
def numba_progress(fn: Callable[[ProgressBar], Generator[int, Any, Any]], *fn_args, **fn_kwargs):
    # FIXME: untested and not finished most likely
    """Usage:
        @numba_progress
        @njit(nogil=True, parallel=True)
        def numba_function(num_iterations, progress_proxy):
            for i in prange(num_iterations):
                #<DO CUSTOM WORK HERE>
                yield 1

    :param fn: Callable[[ProgressBar]:
    :param Generator: int:
    :param Any: param Any]]:
    :param fn: Callable[[ProgressBar]:
    :param Generator[int:
    :param Any]]:
    :param *fn_args:
    :param **fn_kwargs:

    """
    # FIXME (medium): Are you sure numba accept generator function ?
    tqdm_kwargs = {
        # "ncols": 80
    }
    with ProgressBar(dynamic_ncols=True, **tqdm_kwargs) as progress:
        for unit_step in fn(*fn_args, **fn_kwargs):
            progress.update(unit_step or 1)
