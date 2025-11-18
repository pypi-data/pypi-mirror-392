from pathlib import Path


class Stdf4Reader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
