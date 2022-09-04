"""
This file is a collection of data storage mechanisms.
"""

from typing import NamedTuple, Any, Optional
from reprlib import repr as _r


__all__ = ["Tag"]


class Tag(NamedTuple):
    device: str                     #: device address (e.g. "D200")
    value:  Optional[Any] = None    #: value read/written, may be ``None`` on error
    type:   Optional[str] = ''      #: data type of device
    error:  Optional[str] = ''      #: error message if unsuccessful, else ``None``


    def __bool__(self):
        """
        ``True`` if both ``value`` is not ``None`` and ``error`` is ``None``
        ``False`` otherwise
        """
        return self.value is not None and self.error is None


    def __str__(self):
        return f"{self.device}, {_r(self.value)}, {self.type}, {self.error}"


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"device={self.device!r}, "
            f"value={self.value!r}, "
            f"type={self.type!r}, "
            f"error={self.error!r}"
            ")"
        )


class CPUModel(NamedTuple):
    name: str  # name (e.g. 'R08ENCPU')
    code: str  # code (e.g. '4806')


    def __str__(self):
        return f"{self.name}, {self.code}"


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"type={self.name!r}, "
            f"info={self.code!r}"
            ")"
        )


class CPUStatus(NamedTuple):
    status: Optional[str] = ''  # status (e.g. 'Stop')
    cause:  Optional[str] = ''  # cause (e.g. 'By Error')


    def __str__(self):
        return f"{self.status}, {self.cause}"


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"status={self.status!r}, "
            f"cause={self.cause!r}"
            ")"
        )


class LoopbackTest(NamedTuple):
    length: Optional[int] = 0       # length of response
    data:   Optional[str] = None    # reponse data string
