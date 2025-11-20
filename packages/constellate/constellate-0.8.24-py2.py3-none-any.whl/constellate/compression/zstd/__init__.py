try:
    # Prefer pyzstd backend
    from constellate.compression.zstd.pyzstd import ZstdCompressor, ZstdDecompressor
except ImportError:
    # Fallback to zstandard backend
    # Note: zstandard==0.22.0 fails with fatal exception on all py3x versions
    try:
        from constellate.compression.zstd.zstandard import ZstdCompressor, ZstdDecompressor
    except ImportError:
        raise

__all__ = ["ZstdCompressor", "ZstdDecompressor"]
