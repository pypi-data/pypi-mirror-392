from abc import ABC, abstractmethod
from struct import Struct
from typing import Any, ClassVar, Generic, Sequence, TypeVar

from pystdf4.Core.dynamic_buffer import DynamicBuffer
from pystdf4.Core.mixins import CacheMixin

pyT = TypeVar("pyT", int, float, str, bytes)


# ============================================================
# Base Field Abstractions
#     - FieldBase(ABC, Generic[pyT]): Abstract Base Class for all Fields
#         - pack_into(buffer: DynamicBuffer, value: pyT)
#         - unpack_from(buffer_mv: memoryview)
# ============================================================


class FieldBase(ABC, Generic[pyT]):
    @classmethod
    @abstractmethod
    def pack_into(cls, buffer: DynamicBuffer, value: pyT):
        raise NotImplementedError()

    @classmethod
    def unpack_from(cls, buffer_mv: memoryview):
        # TODO: Implement unpack_from at next PR
        raise NotImplementedError()


# ============================================================
# Derived Field Classes
#     - ImmediateField(FieldBase): Immediate write and read of values (e.g. bytes, str, bits, etc.)
#         - pack_into(buffer: DynamicBuffer, value: bytes)
#
#     - DeferredField(FieldBase): Deferred write and read, requires cache management (e.g. int, float, etc.)
#         - pack_into(buffer: DynamicBuffer, value: pyT)
# ============================================================


class ImmediateField(FieldBase[pyT]):
    field_size: ClassVar[int] = 0

    @classmethod
    def pack_into(cls, buffer: DynamicBuffer, value: pyT):
        data = cls._normalize_value(value)
        field_size = cls.field_size if cls.field_size else len(data)
        buffer._ensure_capacity(field_size)
        buffer._mv[buffer.offset : buffer.offset + field_size] = data
        buffer.offset += field_size

    # Utility method
    @staticmethod
    def _pascal_bytes(value: bytes) -> bytes:
        return bytes((len(value),)) + value

    @staticmethod
    @abstractmethod
    def _normalize_value(value: Any) -> bytes:
        raise NotImplementedError()


class DeferredField(FieldBase[pyT], CacheMixin):
    num_elements: ClassVar[int] = 1
    endian: ClassVar[str] = "<"
    field_size: ClassVar[int]
    struct_format: ClassVar[str]

    def __init_subclass__(cls) -> None:
        """Initialize cache and compute element size."""
        super().__init_subclass__()
        cls.field_size = Struct(f"{cls.endian}{cls.num_elements}{cls.struct_format}").size

    @classmethod
    def pack_into(cls, buffer: DynamicBuffer, value: pyT):
        """Reserve space, cache the value, and advance the buffer offset."""
        buffer._ensure_capacity(cls.field_size)
        cls._enqueue_value(value, buffer.offset, cls.field_size)
        buffer.offset += cls.field_size

    @classmethod
    def flush_cache_to_buffer(cls, buffer: DynamicBuffer):
        """Flush cached values to the buffer."""
        cls.flush_cache(memoryview(cls._serialize_sequence(cls.cached_values)), buffer)

    @classmethod
    def _serialize_sequence(cls, sequence: Sequence[pyT]) -> bytes:
        """Pack sequence into bytes using struct."""
        count = len(cls.buffer_offsets) * cls.num_elements
        packer = Struct(f"{cls.endian}{count}{cls.struct_format}")
        return packer.pack(*sequence)
