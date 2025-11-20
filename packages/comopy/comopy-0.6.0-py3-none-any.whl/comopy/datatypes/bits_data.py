# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Abstract base class for all entities carrying logic values.

BitsData provides the data_bits property as an interface to access the logic
value of a circuit net.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from comopy.utils import BitsAssignError

if TYPE_CHECKING:
    from .bits import Bits, Bits1, SignedBits  # pragma: no cover
    from .param_const import ParamConst  # pragma: no cover


class BitsData(ABC):
    """Base class for all bits types.

    Provides .data_bits interface and common right-value operations.
    """

    # Abstract interfaces
    #
    @property
    @abstractmethod
    def data_bits(self) -> Bits:
        """Get the internal Bits data."""

    @property
    @abstractmethod
    def nbits(self) -> int:
        """Get the bit width."""

    # Properties
    #
    @property
    def mutable(self) -> bool:
        """Check if this BitsData is mutable."""
        return True

    @property
    def is_signed(self) -> bool:
        """Check if this BitsData is signed."""
        return False

    # HDL interfaces
    #
    @property
    def S(self) -> SignedBits:
        """Get a signed view of this BitsData."""
        return self.data_bits.S

    @property
    def W(self) -> int:
        """Get the bit width (Verilog $bits())."""
        return self.data_bits.W

    @property
    def N(self) -> Bits1:
        """Check if the signed value is negative (most significant bit)."""
        return self.data_bits.N

    @property
    def AO(self) -> Bits1:
        """Check if all bits are 1 (reduction AND, Verilog &x)."""
        return self.data_bits.AO

    @property
    def NZ(self) -> Bits1:
        """Check if any bit is 1 (reduction OR, Verilog |x)."""
        return self.data_bits.NZ

    @property
    def P(self) -> Bits1:
        """Check parity of bits (reduction XOR, Verilog ^x)."""
        return self.data_bits.P

    @property
    def Z(self) -> Bits1:
        """Check if all bits are 0 (reduction NOR, Verilog ~|x)."""
        return self.data_bits.Z

    def ext(self, nbits: int) -> Bits:
        """Get a width-extended copy of this BitsData."""
        return self.data_bits.ext(nbits)

    # Type conversions
    #
    def __bool__(self) -> bool:
        return bool(self.data_bits)

    def __index__(self) -> int:
        return self.data_bits.__index__()

    # Must provide `__hash__` if `__eq__` is overridden.
    # Defaults to object hash. Bits can be hashed by value, but Signal can't.
    def __hash__(self) -> int:
        return hash(id(self))

    # Assignment
    # Disables all in-place assignments by default.
    #
    def __iadd__(self, other: Any):
        self.__wrong_assignment_type()

    def __isub__(self, other: Any):
        self.__wrong_assignment_type()

    def __imul__(self, other: Any):
        self.__wrong_assignment_type()

    def __imatmul__(self, other: Any):
        self.__wrong_assignment_type()

    def __itruediv__(self, other: Any):
        self.__wrong_assignment_type()

    def __ifloordiv__(self, other: Any):
        self.__wrong_assignment_type()

    def __imod__(self, other: Any):
        self.__wrong_assignment_type()

    def __ipow__(self, other: Any):
        self.__wrong_assignment_type()

    def __iand__(self, other: Any):
        self.__wrong_assignment_type()

    def __ior__(self, other: Any):
        self.__wrong_assignment_type()

    def __ixor__(self, other: Any):
        self.__wrong_assignment_type()

    def __ilshift__(self, other: Any):
        self.__wrong_assignment_type()

    def __irshift__(self, other: Any):
        self.__wrong_assignment_type()

    def __wrong_assignment_type(self):
        raise BitsAssignError(
            self.nbits,
            "wrong assignment type.\n"
            "- Use /= (blocking assignment) or <<= (nonblocking assignment)",
        )

    # Slice
    # By default, rejects slice assignment except for `x[:] /= ...`
    #
    def __setitem__(self, key: Any, value: Any):
        self.__wrong_assignment_type()

    # Arithmetics
    # - Support (BitsData __op__ BitsData|ParamConst|int).
    # - ParamConst handles (ParamConst __op__ BitsData).
    #
    def __add__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__add__(other)

    def __radd__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__radd__(other)

    def __sub__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__sub__(other)

    def __rsub__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__rsub__(other)

    def __mul__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__mul__(other)

    def __rmul__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__rmul__(other)

    def __pos__(self) -> Bits:
        return self.data_bits.__pos__()

    def __neg__(self) -> Bits:
        return self.data_bits.__neg__()

    # Bitwise operations
    # - Support (BitsData __op__ BitsData|ParamConst|int)
    # - ParamConst handles (ParamConst __op__ BitsData).
    #
    def __and__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__and__(other)

    def __rand__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__rand__(other)

    def __or__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__or__(other)

    def __ror__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__ror__(other)

    def __xor__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__xor__(other)

    def __rxor__(self, other: Any) -> Bits | ParamConst:
        return self.data_bits.__rxor__(other)

    def __invert__(self) -> Bits:
        return self.data_bits.__invert__()

    # Shifts
    # Support (BitsData __op__ BitsData|int), return a new Bits.
    #
    # No type hint for return value, avoiding conflict with <<=
    def __lshift__(self, other: Any):
        return self.data_bits.__lshift__(other)

    def __rshift__(self, other: Any) -> Bits:
        return self.data_bits.__rshift__(other)

    # Comparison
    # Support (BitsData __op__ BitsData|int), return a new Bits1.
    #
    def __eq__(self, other: Any) -> Bits1:  # type: ignore
        return self.data_bits.__eq__(other)

    def __ne__(self, other: Any) -> Bits1:  # type: ignore
        return self.data_bits.__ne__(other)

    def __lt__(self, other: Any) -> Bits1:
        return self.data_bits.__lt__(other)

    def __le__(self, other: Any) -> Bits1:
        return self.data_bits.__le__(other)

    def __gt__(self, other: Any) -> Bits1:
        return self.data_bits.__gt__(other)

    def __ge__(self, other: Any) -> Bits1:
        return self.data_bits.__ge__(other)
