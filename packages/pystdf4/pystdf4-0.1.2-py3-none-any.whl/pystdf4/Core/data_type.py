from pystdf4.Core.data_base import ArrayField, DeferredField, ImmediateField

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


class C_1(ImmediateField[str]):
    field_size = 1

    @staticmethod
    def _normalize_value(value: str, size: int = 0) -> bytes:
        return value.encode("ascii")


class C_12(ImmediateField[str]):
    field_size = 12

    @staticmethod
    def _normalize_value(value: str, size: int = 0) -> bytes:
        return value.encode("ascii")


class B_1(ImmediateField[bytes]):
    field_size = 1

    @staticmethod
    def _normalize_value(value: bytes, size: int = 0) -> bytes:
        return value


class B_6(ImmediateField[bytes]):
    field_size = 6

    @staticmethod
    def _normalize_value(value: bytes, size: int = 0) -> bytes:
        return value


class C_n(ImmediateField[str]):
    @staticmethod
    def _normalize_value(value: str, size: int = 0) -> bytes:
        return ImmediateField._pascal_bytes(value.encode("ascii"))


class B_n(ImmediateField[bytes]):
    @staticmethod
    def _normalize_value(value: bytes, size: int = 0) -> bytes:
        return ImmediateField._pascal_bytes(value)


class C_f(ImmediateField[str]):
    @staticmethod
    def _normalize_value(value: bytes, size: int = 0) -> bytes:
        return ImmediateField._left_justified_bytes(value, size, b" ")


# ============================================================
# Array Field Implementations
# ============================================================


class kxU_1(ArrayField):
    element_type = U_1


class kxU_2(ArrayField):
    element_type = U_2


class kxC_n(ArrayField):
    element_type = C_n


class kxR_4(ArrayField):
    element_type = R_4


# TODO: Implement N_1 field!
# class kxN_1(ArrayField):
#     element_type = N_1
