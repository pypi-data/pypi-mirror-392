import sys

import pytest
from pyexpect import expect

has_min_python_version=sys.version_info >= (3, 11)

if has_min_python_version:
    from constellate.cli.argument.unparse import to_arg_unparse
else:
    def to_arg_unparse(**kwargs) -> list[str]:
        return []


@pytest.mark.parametrize(
    "test_case",
    [
        (
            {
                "command": "cmd",
                "sub_command": "sub",
                "options": {"foo": True, "bar": "baz"},
                "arguments": ["file.txt"],
            },
            ["cmd", "sub", "--foo", "--bar=baz", "file.txt"],
        ),
        (
            {
                "command": "cmd",
                "sub_command": "sub",
                "options": ["foo", True, "bar", "baz", "bar", "baz2"],
                "arguments": ["file.txt"],
            },
            ["cmd", "sub", "--foo", "--bar=baz", "--bar=baz2", "file.txt"],
        ),
    ],
)
@pytest.mark.skipif(not has_min_python_version, reason="requires python 3.11+")
def test_to_argument_unparse(test_case) -> None:
    expect(
        to_arg_unparse(
            command=test_case[0]["command"],
            sub_command=test_case[0]["sub_command"],
            options=test_case[0]["options"],
            arguments=test_case[0]["arguments"],
        )
    ).to_equal(test_case[1])
