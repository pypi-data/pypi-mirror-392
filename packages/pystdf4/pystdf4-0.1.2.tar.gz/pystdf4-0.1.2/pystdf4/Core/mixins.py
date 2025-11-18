from typing import Any, ClassVar

from pystdf4.Core.dynamic_buffer import DynamicBuffer

# ============================================================
# Cache Mixin
# ============================================================


class CacheMixin:
    """
    Provides per-class caching functionality for deferred buffer writes.
    """

    buffer_offsets: ClassVar[list]
    cached_values: ClassVar[list]
    cached_sizes: ClassVar[list]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # Ensure each subclass has its own cache
        cls.buffer_offsets = []
        cls.cached_values = []
        cls.cached_sizes = []

    @classmethod
    def _enqueue_value(cls, value: Any, offset: int, size: int):
        """Cache a value and its buffer offset."""
        cls.buffer_offsets.append(offset)
        cls.cached_values.append(value)
        cls.cached_sizes.append(size)

    @classmethod
    def flush_cache(cls, packed_mv: memoryview, buffer: DynamicBuffer):
        """Flush cached values into buffer using `field_size`."""
        if not cls.buffer_offsets:
            return

        cursor = 0
        for offset, size in zip(cls.buffer_offsets, cls.cached_sizes):
            buffer._mv[offset : offset + size] = packed_mv[cursor : cursor + size]
            cursor += size

        cls.buffer_offsets.clear()
        cls.cached_values.clear()
        cls.cached_sizes.clear()
