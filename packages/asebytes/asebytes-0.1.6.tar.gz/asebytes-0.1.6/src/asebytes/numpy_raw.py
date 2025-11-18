"""
Raw numpy array serialization for maximum read performance.

This module provides fast serialization/deserialization of numpy arrays
by storing them as raw bytes with a compact binary header containing
dtype and shape information.

Performance: ~2x faster reads compared to msgpack serialization.
"""

import struct

import numpy as np


def encode_numpy(arr: np.ndarray) -> bytes:
    """
    Encode numpy array as raw bytes with inline metadata header.

    Format:
    - dtype_len (uint8): Length of dtype string
    - dtype_str (bytes): Dtype string (e.g., b'<f8')
    - ndim (uint8): Number of dimensions
    - shape (int64 * ndim): Shape tuple
    - data (raw bytes): Array data via tobytes()

    Args:
        arr: Numpy array to encode

    Returns:
        bytes: Encoded array data

    Example:
        >>> arr = np.array([[1.0, 2.0, 3.0]], dtype=np.float64)
        >>> data = encode_numpy(arr)
        >>> decoded = decode_numpy(data)
        >>> np.array_equal(arr, decoded)
        True
    """
    # Get dtype string (e.g., '<f8' for little-endian float64)
    dtype_str = arr.dtype.str.encode("ascii")
    dtype_len = len(dtype_str)

    if dtype_len > 255:
        raise ValueError(f"Dtype string too long: {len(dtype_str)} bytes")

    if arr.ndim > 255:
        raise ValueError(f"Too many dimensions: {arr.ndim}")

    # Build header
    header = bytearray()
    header.append(dtype_len)  # 1 byte
    header.extend(dtype_str)  # variable length
    header.append(arr.ndim)  # 1 byte

    # Pack shape as int64 values (8 bytes each)
    for dim in arr.shape:
        header.extend(struct.pack("<q", dim))  # little-endian int64

    # Append raw array data
    return bytes(header) + arr.tobytes()


def decode_numpy(data: bytes, copy: bool = True) -> np.ndarray:
    """
    Decode numpy array from raw bytes with inline metadata header.

    Args:
        data: Encoded array bytes
        copy: If True, return writable copy. If False, return read-only view (faster, less memory)

    Returns:
        np.ndarray: Decoded array

    Example:
        >>> arr = np.array([[1.0, 2.0, 3.0]], dtype=np.float64)
        >>> data = encode_numpy(arr)
        >>> decoded = decode_numpy(data, copy=False)  # Fast, read-only
        >>> decoded.flags.writeable
        False
    """
    offset = 0

    # Read dtype length
    dtype_len = data[offset]
    offset += 1

    # Read dtype string
    dtype_str = data[offset : offset + dtype_len].decode("ascii")
    offset += dtype_len

    # Read ndim
    ndim = data[offset]
    offset += 1

    # Read shape
    shape = []
    for _ in range(ndim):
        dim = struct.unpack("<q", data[offset : offset + 8])[0]
        shape.append(dim)
        offset += 8

    # Create dtype object
    dtype = np.dtype(dtype_str)

    # Decode array from remaining bytes
    # Use frombuffer for zero-copy operation
    arr = np.frombuffer(data, dtype=dtype, offset=offset)

    # Reshape
    if shape:
        arr = arr.reshape(shape)

    # Make writable copy if requested
    if copy:
        arr = arr.copy()
    else:
        # Explicitly mark as read-only for safety
        arr.flags.writeable = False

    return arr


def is_numpy_array(obj) -> bool:
    """Check if object is a numpy array."""
    return isinstance(obj, np.ndarray)


def get_header_size(data: bytes) -> int:
    """
    Calculate the size of the header in encoded numpy data.

    Useful for advanced zero-copy operations.

    Args:
        data: Encoded array bytes

    Returns:
        int: Size of header in bytes
    """
    offset = 0

    # Read dtype length
    dtype_len = data[offset]
    offset += 1

    # Skip dtype string
    offset += dtype_len

    # Read ndim
    ndim = data[offset]
    offset += 1

    # Skip shape (8 bytes per dimension)
    offset += ndim * 8

    return offset
