from zstandard import ZstdCompressor as _ZstdCompressor
from zstandard import ZstdDecompressor as _ZstdDecompressor
from zstandard import ZstdCompressionParameters as _ZstdCompressionParameters

from constellate.compression.zstd.common import (
    ZstdCompressorProtocol,
    ZstdCompressionParameters,
    DataInput,
    DataOutput,
    ZstdDecompressorProtocol,
)


class ZstdCompressor(ZstdCompressorProtocol):
    def __init__(self, parameters: ZstdCompressionParameters = None):
        self._compressor = _ZstdCompressor(
            compression_params=_ZstdCompressionParameters(
                compression_level=parameters.level,
                write_checksum=parameters.write_checksum,
                write_content_size=parameters.write_content_size,
                threads=parameters.threads,
            )
        )
        self._parameters = parameters

    def compress(self, data: DataInput = None) -> bytes:
        if isinstance(data, str):
            if self._parameters.encoder is None:
                raise ValueError()
            data2, _ = self._parameters.encoder.encode(data)
            return self._compressor.compress(data2)

        return self._compressor.compress(data)


class ZstdDecompressor(ZstdDecompressorProtocol):
    def __init__(self, parameters: ZstdCompressionParameters = None):
        super().__init__()
        self._decompressor = _ZstdDecompressor()
        self._parameters = parameters

    def decompress(self, data: bytes = None) -> DataOutput:
        data2 = self._decompressor.decompress(data)
        if self._parameters.decoder is not None:
            data3, _ = self._parameters.decoder.decode(data2)
            return data3

        return data2


__all__ = ["ZstdCompressor", "ZstdDecompressor"]
