import os
import tempfile
from pathlib import Path

import pytest
from pyexpect import expect

from constellate.storage.filesystem.tmpfs.rambacked import mkd_tmpfs


@pytest.mark.parametrize(
    "test_case",
    [
        (
            {
                "prefix": "prefixed",
                "suffix": "suffixed",
            },
            None,
        ),
        (
            {
                "dir": "/tmp/tour",
            },
            None,
        ),
        (
            {
                "env_tmpfs_dir": "TMPFS_TEST_DIR",
                "env_tmpfs_dir_fs_types": [
                    "ext4",
                    "overlay",
                    "tmpfs",
                ],  # tmpfs: workstation-server-vm0, "overlay/ext4": memory/ext4 backed volume on docker container
            },
            None,
        ),
    ],
)
def test_mkd_tmpfs(test_case) -> None:
    data = test_case[0]

    def case_data(keys):
        for key in keys:
            if key in data:
                yield (key, data[key])

    # Create dir as required
    for _key, value in case_data(["dir"]):
        Path(value).mkdir(exist_ok=True)

    # Create dir associated to env_tmpfs_dir as required
    for key, value in case_data(["env_tmpfs_dir"]):
        os.environ[value] = tempfile.mkdtemp()

    # Create tmpfs dir
    with mkd_tmpfs(**data) as tmp_dir_path:
        # Test prefix / suffix presences
        for key, value in case_data(["prefix", "suffix"]):
            expect(value in tmp_dir_path).true()

        for key, value in case_data(["dir"]):
            expect(tmp_dir_path.startswith(value)).true()

        for key, value in case_data(["env_tmpfs_dir"]):
            expect(tmp_dir_path.startswith(os.environ[value])).true()
