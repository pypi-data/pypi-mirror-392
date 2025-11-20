import sys
from contextlib import contextmanager, nullcontext
from unittest.mock import patch


@contextmanager
def mock_sys_argv(argv: list[str] = None):
    argv_context_manager = (
        nullcontext(enter_result=None) if argv is None else patch.object(sys, "argv", argv)
    )
    with argv_context_manager as argv_mock:
        yield argv_mock
