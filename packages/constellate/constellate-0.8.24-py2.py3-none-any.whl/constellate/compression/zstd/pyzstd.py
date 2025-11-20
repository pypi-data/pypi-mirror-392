from pyzstd import compress as _compress
from pyzstd import decompress as _decompress
from pyzstd import CParameter as _CParameter

from constellate.compression.zstd.common import (
    ZstdCompressorProtocol,
    ZstdCompressionParameters,
    DataInput,
    DataOutput,
    ZstdDecompressorProtocol,
)


class ZstdCompressor(ZstdCompressorProtocol):
    def __init__(self, parameters: ZstdCompressionParameters = None):
        self._parameters = parameters

    def compress(self, data: DataInput = None) -> bytes:
        if isinstance(data, str):
            if self._parameters.encoder is None:
                raise ValueError()
            data2, _ = self._parameters.encoder.encode(data)
            return _compress(
                data2,
                level_or_option={
                    _CParameter.compressionLevel: self._parameters.level,
                    _CParameter.checksumFlag: 0 if self._parameters.write_checksum else 1,
                    _CParameter.contentSizeFlag: 0 if self._parameters.write_content_size else 1,
                    _CParameter.nbWorkers: self._parameters.threads,
                },
            )

        return _compress(
            data,
            level_or_option={
                _CParameter.compressionLevel: self._parameters.level,
                _CParameter.checksumFlag: 0 if self._parameters.write_checksum else 1,
                _CParameter.contentSizeFlag: 0 if self._parameters.write_content_size else 1,
                _CParameter.nbWorkers: self._parameters.threads,
            },
        )


class ZstdDecompressor(ZstdDecompressorProtocol):
    def __init__(self, parameters: ZstdCompressionParameters = None):
        self._parameters = parameters

    def decompress(self, data: bytes = None) -> DataOutput:
        data2 = _decompress(data, option={})
        if self._parameters.decoder is not None:
            data3, _ = self._parameters.decoder.decode(data2)
            return data3

        return data2


__all__ = ["ZstdCompressor", "ZstdDecompressor", "ZstdCompressionParameters"]
