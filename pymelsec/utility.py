"""
File hold various utility functions
"""

import re

def get_device_index(device:str) -> str:
    """
    Extract device index.

    Args:
        device(str):    device memory space (e.g. "D1000")
    Returns:
        device_index(str): device memory index (e.g. "1000")
    Example:
        "D1000" -> "1000"
        "X0x1A" -> "0x1A"
    """
    device_num = re.search(r"\d.*", device)
    if device_num is None:
        raise ValueError(f'Invalid device index "{device}"')
    return device_num.group(0)


def get_device_type(device:str) -> str:
    """
    Extract device type.

    Args:
        device(str):    device memory space (e.g. "D1000")
    Returns:
        device_index(str): device memory index (e.g. "D")
    Example:
        "D1000" -> "D"
        "X0x1A" -> "X0"
    """
    device_type = re.search(r"\D+", device)
    if device_type is None:
        raise ValueError(f'Invalid device type "{device}"')
    return device_type.group(0)
