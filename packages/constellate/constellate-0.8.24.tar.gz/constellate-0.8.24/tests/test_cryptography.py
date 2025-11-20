from pathlib import Path

import pytest
from pyexpect import expect

from constellate.cryptography.digest.hexadecimal import hexadecimal


@pytest.mark.parametrize("family", ["blake3", "sha256"])
@pytest.mark.parametrize("input_type", [str, bytes, Path])
def test_hexadecimal(family, input_type, tmp_path) -> None:
    digest = {
        "blake3": "df73ed30dfca8453d22dadd125c496d6fd823b0d6dd7e9772083606d2774569c",
        "sha256": "0301844ccd8e9ca705291e7aacd1053a4cf9987d4843d6d5c91985df9c3f96ab",
    }.get(family, "missing")

    input = "footer"
    if input_type is str:
        pass
    elif input_type is bytes:
        input = input.encode("utf-8")
    elif input_type is Path:
        f = tmp_path / "file.txt"
        f.write_text(input, encoding="utf-8")
        input = Path(f)

    expect(hexadecimal(family=family, value=input)).to_equal(digest)
