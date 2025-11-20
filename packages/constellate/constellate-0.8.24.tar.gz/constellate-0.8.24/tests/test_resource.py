from pyexpect import expect
from .data import test_resource as test_resource_pkg

from constellate.resource.resource import get_folder, get_files


def test_resource() -> None:
    expect(str(get_folder(root_pkg_name=test_resource_pkg.__package__, directory="foo"))).contains(
        "data/test_resource/foo"
    )
    expect(
        str(get_files(root_pkg_name=test_resource_pkg.__package__, directory="foo")[0])
    ).contains("data/test_resource/foo/bar.txt")
