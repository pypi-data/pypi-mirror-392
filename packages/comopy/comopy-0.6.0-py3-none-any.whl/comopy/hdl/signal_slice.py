# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
A slice of a connectable signal object.

SignalSlice tracks the owning BitsData and the slice range, ensuring correct
assignment within signal bundles.
"""

from typing import Any

from comopy.datatypes import Bits, BitsData, ParamConst
from comopy.utils import BitsAssignError

from .connectable import Connectable


class SignalSlice(Connectable):

    _owner: Connectable
    _key: Any
    _nbits: int

    def __init__(self, owner: Connectable, key: Any):
        super().__init__()
        assert isinstance(owner, Connectable)
        assert not isinstance(owner, SignalSlice), "No SignalSlice[] by now"
        self._owner = owner
        self._key = key
        self._nbits = self.data_driven.nbits

    # BitsData
    #
    @property
    def data_bits(self) -> Bits:
        return self._owner.data_bits[self._key]

    @property
    def nbits(self) -> int:
        return self._nbits

    @property
    def mutable(self) -> bool:
        return self._owner.mutable

    # Connectable
    #
    @property
    def data_driven(self) -> Bits:
        return self._owner.data_driven[self._key]

    @data_driven.setter
    def data_driven(self, value: Bits | int):
        assert isinstance(value, (Bits, int))
        driven = self._owner.data_driven
        driven[self._key] = value
        # Call the setter. Don't assign to the Bits returned by the getter.
        self._owner.data_driven = driven

    # Properties
    #
    @property
    def owner(self) -> Connectable:
        return self._owner

    @property
    def key(self) -> Any:
        return self._key

    # Assignment
    #
    # /= : blocking assignment
    def __itruediv__(self, value: Any):
        owner = self._owner
        n = owner.nbits
        if not owner.mutable:
            slice_of = "" if self.__is_all_slice() else "slice of "
            raise BitsAssignError(n, f"{slice_of}immutable Bits{n}")

        if isinstance(value, ParamConst):
            value = value.param_value
        if isinstance(value, BitsData):
            value = value.data_bits
        new_data = Bits(n, owner.data_bits, mutable=True)
        new_data[self._key] = value
        owner /= new_data  # type: ignore
        return self

    def __is_all_slice(self) -> bool:
        if isinstance(self._key, slice):
            return self._key.start is None and self._key.stop is None
        return False

    # <<= : nonblocking assignment
    def __ilshift__(self, value: Any):
        owner = self._owner
        n = owner.nbits
        if not owner.mutable:
            slice_of = "" if self.__is_all_slice() else "slice of "
            raise BitsAssignError(n, f"{slice_of}immutable Bits{n}")

        if isinstance(value, ParamConst):
            value = value.param_value
        if isinstance(value, BitsData):
            value = value.data_bits
        new_data = Bits(n, owner.data_bits._next, mutable=True)
        new_data[self._key] = value
        owner <<= new_data  # type: ignore
        return self

    # @= : continuous assignment (connection)
    def __imatmul__(self, value: BitsData | int):
        if not self._owner.mutable:
            n = self._owner.nbits
            slice_of = "" if self.__is_all_slice() else "slice of "
            raise BitsAssignError(n, f"{slice_of}immutable Bits{n}")
        return Connectable.__imatmul__(self, value)
