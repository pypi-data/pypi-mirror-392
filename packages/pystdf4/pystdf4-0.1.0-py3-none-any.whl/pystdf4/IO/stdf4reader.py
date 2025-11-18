from .base import StdfIOBase


class Stdf4Reader(StdfIOBase):
    def __init__(self, file_path: str):
        super().__init__(file_path)
