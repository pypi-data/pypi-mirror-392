from pystdf4.Core.data_base import DeferredField, ImmediateField

# ============================================================
# Numeric Field Implementations
# ============================================================


class U_1(DeferredField[int]):
    struct_format = "B"


class U_2(DeferredField[int]):
    struct_format = "H"


class U_4(DeferredField[int]):
    struct_format = "I"


class I_1(DeferredField[int]):
    struct_format = "b"


class I_2(DeferredField[int]):
    struct_format = "h"


class I_4(DeferredField[int]):
    struct_format = "i"


class R_4(DeferredField[float]):
    struct_format = "f"


class R_8(DeferredField[float]):
    struct_format = "d"


# ============================================================
# Byte-like Field Implementations
# ============================================================


class C_1(ImmediateField):
    field_size = 1

    @staticmethod
    def _normalize_value(value: str) -> bytes:
        return value.encode("ascii")


class B_1(ImmediateField):
    field_size = 1

    @staticmethod
    def _normalize_value(value: bytes) -> bytes:
        return value


class C_n(ImmediateField):
    @staticmethod
    def _normalize_value(value: str) -> bytes:
        return ImmediateField._pascal_bytes(value.encode("ascii"))


class B_n(ImmediateField):
    @staticmethod
    def _normalize_value(value: bytes) -> bytes:
        return ImmediateField._pascal_bytes(value)
