from enum import IntEnum, auto, IntFlag, Flag

import pytest
from pyexpect import expect

from constellate.datatype.enum.enum import has_flag


class Inc(IntEnum):
    A = auto()
    B = auto()
    C = auto()


class F(Flag):
    A = auto()
    B = auto()
    C = auto()


class IF(IntFlag):
    A = auto()
    B = auto()
    C = auto()


def test_enum_has_flag() -> None:
    # Verify appropriate arguments types are used
    with pytest.raises(ValueError):
        has_flag(Inc.A, Inc.A)
    with pytest.raises(ValueError):
        has_flag(Inc.A, Inc.A | Inc.B)
    with pytest.raises(ValueError):
        has_flag(None, Inc.A)

    # Verify requested single flag is detected
    expect(has_flag(F.A, F.A)).to_be(True)
    expect(has_flag(IF.A, IF.A)).to_be(True)

    # Verify requested single flag is detected
    expect(has_flag(F.A | F.B, F.A)).to_be(True)
    expect(has_flag(IF.A | IF.B, IF.A)).to_be(True)

    # Verify requested multi flag is detected
    expect(has_flag(F.A | F.B, F.A | F.B)).to_be(True)
    expect(has_flag(IF.A | IF.B, IF.A | IF.B)).to_be(True)

    # Verify requested single flag is not detected
    expect(has_flag(F.A, F.C)).to_be(False)
    expect(has_flag(IF.A, IF.C)).to_be(False)

    # Verify requested multi flag is not detected
    expect(has_flag(F.C, F.A | F.B)).to_be(False)
    expect(has_flag(IF.C, IF.A | IF.B)).to_be(False)
