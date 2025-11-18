from struct import Struct
from typing import Callable, Tuple

from pystdf4.Core import B_1, C_1, I_1, I_2, I_4, R_4, R_8, U_1, U_2, U_4, B_n, C_n, DynamicBuffer, kxC_n, kxR_4, kxU_1, kxU_2


class RecordBase:
    def __init__(self):
        self.buffer = DynamicBuffer()
        self.header_packer: Struct = Struct("<HBB")

        self.B_1 = B_1()
        self.C_1 = C_1()
        self.I_1 = I_1()
        self.I_2 = I_2()
        self.I_4 = I_4()
        self.R_4 = R_4()
        self.R_8 = R_8()
        self.U_1 = U_1()
        self.U_2 = U_2()
        self.U_4 = U_4()
        self.B_n = B_n()
        self.C_n = C_n()
        self.kxC_n = kxC_n()
        self.kxR_4 = kxR_4()
        self.kxU_1 = kxU_1()
        self.kxU_2 = kxU_2()

    def write_fields(self, rec_typ: int, rec_sub: int, field_writer: Callable):
        # Step 1: Write the header of the record
        record_start = self._write_header((rec_typ, rec_sub))

        # Step 2: Write the fields of the record
        field_writer(self)

        # Step 3: Update the length of the record
        record_end = self.buffer.offset
        record_length = record_end - (record_start + 4)
        self.buffer._mv[record_start : record_start + 2] = record_length.to_bytes(2, byteorder="little")

    def _write_header(self, header: Tuple[int, int]) -> int:
        """
        Write the header of a record to the file.
        """
        packer_size = self.header_packer.size
        self.buffer._ensure_capacity(packer_size)
        start = self.buffer.offset
        self.header_packer.pack_into(self.buffer._mv, start, 0, *header)
        self.buffer.offset += packer_size
        return start
