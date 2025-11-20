from constellate.compression.zstd import ZstdCompressor, ZstdDecompressor
from constellate.compression.zstd.common import ZstdCompressionParameters
from pyexpect import expect
import pytest


# def test_compress_decompress_ram_zip(tmp_path) -> None:
#     original_name = "original.txt"
#     local_file_path = tmp_path / original_name
#     with open(local_file_path, 'w', encoding='utf-8') as f:
#         f.write("hello")
#
#     zip_file_info = ZipFileInfo( root=tmp_path, data_zip_info=ZipInfo.from_file( filename=str(local_file_path)))
#     config = create_ram_zip(compression=ZIP_BZIP2)
#     zip_config = append_ram_zip(config=config, files=[zip_file_info])
#
#     local_file_path2 = tmp_path / "decompressed.txt"
#     zip_config.save_ram_zip(file_path=Path(local_file_path2), config=zip_config)
#
#     with open(local_file_path2, 'w', encoding='utf-8') as f:
#         f.write("hello")
#
# expect(zip_config.buffer).to_be("home")


@pytest.mark.parametrize("data", ["hello", b"hello"])
def test_compress_decompress_zstd(data) -> None:
    params = None
    if isinstance(data, str):
        params = ZstdCompressionParameters()
    elif isinstance(data, bytes):
        params = ZstdCompressionParameters(encoder=None, decoder=None)

    compressor = ZstdCompressor(parameters=params)
    decompressor = ZstdDecompressor(parameters=params)

    expect(decompressor.decompress(compressor.compress(data))).to_equal(data)
