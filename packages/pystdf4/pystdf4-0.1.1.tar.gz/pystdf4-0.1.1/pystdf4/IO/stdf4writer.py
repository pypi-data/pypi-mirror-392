from pathlib import Path

from pystdf4.Records.packer import StdfPacker


class Stdf4Writer(StdfPacker):
    # region Magic Methods
    def __init__(self, file_path: str):
        super(StdfPacker, self).__init__()
        self.file_path = Path(file_path)

    def __enter__(self) -> "Stdf4Writer":
        if not self.file_path.exists():
            self.file_path.touch()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        self._write_buffers()
        self.file_path.write_bytes(self.buffer.to_bytes())

    # endregion

    def _write_buffers(self):
        for scalar_field in (
            self.U_1,
            self.U_2,
            self.U_4,
            self.I_1,
            self.I_2,
            self.I_4,
            self.R_4,
            self.R_8,
        ):
            scalar_field.flush_cache_to_buffer(self.buffer)
