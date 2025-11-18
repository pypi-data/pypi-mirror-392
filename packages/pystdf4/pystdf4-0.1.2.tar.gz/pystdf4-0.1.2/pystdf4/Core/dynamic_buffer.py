class DynamicBuffer:
    """
    High-performance dynamically resizable byte buffer.

    This class is designed for low-level binary data construction (e.g., STDF or protocol records).
    It provides in-place memory writes, safe resizing, and minimal object creation overhead.
    """

    __slots__ = ("_buffer", "_mv", "_capacity", "offset")

    def __init__(self, initial_capacity: int = 1024**2):
        """
        Initialize the buffer.

        Args:
            initial_capacity (int): Initial memory capacity in bytes.
        """
        self._buffer = bytearray(initial_capacity)
        self.offset = 0
        self._mv = memoryview(self._buffer)
        self._capacity = initial_capacity

    # region properties
    @property
    def capacity(self) -> int:
        """Current capacity of the buffer."""
        return self._capacity

    @capacity.setter
    def capacity(self, value: int) -> None:
        """
        Resize the buffer to the given capacity.

        Raises:
            ValueError: If the new capacity is smaller than the current offset.
        """
        if value < self.offset:
            raise ValueError(f"Cannot shrink below current offset ({self.offset} bytes)")

        new_buf = bytearray(value)
        new_buf[: self.offset] = self._buffer[: self.offset]
        self._buffer = new_buf
        self._mv = memoryview(new_buf)
        self._capacity = value

    def __len__(self) -> int:
        """Number of valid bytes written to the buffer."""
        return self.offset

    def __repr__(self) -> str:
        return f"<DynamicBuffer offset={self.offset} capacity={self._capacity}>"

    # endregion

    # region private methods

    def _ensure_capacity(self, size: int):
        """
        Ensure sufficient capacity for the next write of `size` bytes.
        """
        if (target := self.offset + size) > self._capacity:
            # Expand at least double or fit the target size
            desired = self._capacity
            while desired < target:
                desired = (desired * 3 + 1) >> 1  # ~1.5x growth
            self.capacity = desired

    # endregion

    # region read / export operations

    def to_bytes(self) -> bytes:
        """Return the valid data as immutable bytes."""
        return self._mv[: self.offset].tobytes()

    # endregion
