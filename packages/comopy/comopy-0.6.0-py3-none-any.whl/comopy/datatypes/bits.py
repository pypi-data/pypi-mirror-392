# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Data type for fixed-width bit vector.

Bits is the base type for all BitsData types.
Bits is immutable by default and is also used for literal constants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Type

from comopy.utils import BitsAssignError, BitsWidthError

from .bit_pat import BitPat
from .bits_data import BitsData
from .param_const import ParamConst

if TYPE_CHECKING:
    from comopy.hdl.signal_bundle import SignalBundle

_bits_nmax = 1025
_bits_mask = [0] + [(1 << k) - 1 for k in range(1, _bits_nmax + 1)]
_bits_mins = [0] + [(-1) << (k - 1) for k in range(1, _bits_nmax + 1)]


def _check_nbits(nbits: int, value: int):
    high = _bits_mask[nbits]  # max for unsigned
    low = _bits_mins[nbits]  # min for signed
    if value < low or value > high:
        raise ValueError(
            f"{value} ({hex(value)}) is too wide for {nbits} bits, "
            f"valid range: [{low}, {high}] ([{hex(low)}, {hex(high)}])."
        )


def _trunc_bits(value: int, nbits: int) -> int:
    return int(value) & _bits_mask[nbits]


# Bypass checks for a new Bits.
# No type hint for dynamic Bits<N>.
def _new_valid_bits(nbits: int, value: int, mutable: bool = False):
    assert isinstance(nbits, int) and 1 <= nbits <= _bits_nmax
    assert isinstance(value, int)
    # Convert bool to int to avoid DeprecationWarning in __int__()
    if isinstance(value, bool):
        value = int(value)
    cls = Bits._bits_types.get(nbits)
    if not cls:
        Bits(nbits)  # Create the subclass
        cls = Bits._bits_types[nbits]
    assert issubclass(cls, Bits)
    bits = object.__new__(cls)
    bits._nbits = nbits
    bits._uint = value
    bits._next = value
    bits._last = value
    bits._mutable = mutable
    return bits


class Bits(BitsData):
    """Data type for fixed-width bits.

    Bits is also a class factory that dynamically creates subclasses Bits<N>
    for different bit widths. This allows bit widths to be compared by
    checking the types directly. The subclass Bits<N> is a singleton for each
    bit width N. This feature is crucial to support the class capture pattern
    in match statements.
    """

    # Dynamic subclasses for different bit widths.
    _bits_types: dict[int, Type[Bits]] = {}

    # Instance attributes
    __slots__ = ("_nbits", "_uint", "_next", "_last", "_mutable")

    # In match-case, match width by subclass and match value in pattern.
    __match_args__ = ("_uint",)

    # Dynamically create subclass singleton for N bits.
    # This enables checking bit widths by comparing types.
    def __new__(cls, *args, **kwargs):

        # __init__ for Bits subclasses: __init__(value=0, *, mutable=False)
        def sub_init(self, *args, **kwargs):
            if hasattr(self, "_init_args"):
                # Called from Bits.__new__
                assert args[0] == nbits or args[0].param_value == nbits
                args = self._init_args
            Bits.__init__(self, nbits, *args, **kwargs)

        if cls != Bits:
            return super(Bits, cls).__new__(cls)

        if len(args) < 1:
            raise TypeError(
                "Bits.__new__() requires at least one argument: 'nbits'."
            )
        nbits = args[0]
        if isinstance(nbits, ParamConst):
            width_param = nbits
            nbits = nbits.param_value
        else:
            width_param = ParamConst(nbits)
        if not isinstance(nbits, int):
            raise TypeError(
                "Bits.__new__() expects an integer for the 'nbits' argument."
            )
        if nbits < 1 or nbits > _bits_nmax:
            raise ValueError(
                f"No Bits({nbits}), nbits in [1, {_bits_nmax}] only."
            )

        subclass = cls._bits_types.get(nbits)
        if not subclass:
            subclass = type(
                f"Bits{nbits}",
                (cls,),
                {"__init__": sub_init, "__module__": cls.__module__},
            )
            cls._bits_types[nbits] = subclass
        inst = super(Bits, subclass).__new__(subclass)
        inst._init_args = args[1:]
        inst._width_param = width_param
        return inst

    # Pass *args, **kwargs to support dynamic subclasses.
    # __init__(nbits, value=0, *, mutable=False) -> Bits
    def __init__(self, *args, **kwargs):
        nbits = args[0]
        assert isinstance(nbits, int)
        self._nbits = nbits
        self._mutable = kwargs.get("mutable", False)

        value = args[1] if len(args) > 1 else 0
        if isinstance(value, Bits):
            if nbits != value._nbits:
                raise ValueError(
                    f"Width mismatch for constructing Bits{nbits} from "
                    f"Bits{value._nbits}."
                    "\n- Use .ext(width), .S.ext(width), "
                    "or slice [:width] to match widths."
                )
            self._uint = value._uint
        elif isinstance(value, int):
            value = int(value)
            _check_nbits(nbits, value)
            self._uint = _trunc_bits(value, nbits)
        else:
            raise TypeError(
                f"Wrong type {type(value)} to construct Bits{nbits}."
            )
        self._next = self._uint
        self._last = self._uint

    # BitsData
    #
    @property
    def data_bits(self) -> Bits:
        return self

    @property
    def nbits(self) -> int:
        return self._nbits

    @property
    def mutable(self) -> bool:
        return self._mutable

    # Properties
    #
    @property
    def unsigned(self) -> int:
        return self._uint

    @property
    def signed(self) -> int:
        if self._uint >> (self._nbits - 1):
            return -int(_trunc_bits(~self._uint, self._nbits) + 1)
        return self._uint

    @property
    def width_param(self) -> ParamConst:
        if not hasattr(self, "_width_param"):
            self._width_param = ParamConst(self._nbits)
        assert isinstance(self._width_param, ParamConst)
        return self._width_param

    # HDL interfaces
    #
    @property
    def S(self) -> SignedBits:
        return SignedBits(self._nbits, self._uint)

    @property
    def W(self) -> int:
        return self._nbits

    @property
    def N(self) -> Bits1:
        msb = self._uint >> (self._nbits - 1)
        return _new_valid_bits(1, msb)

    @property
    def AO(self) -> Bits1:
        return self == (1 << self._nbits) - 1

    @property
    def NZ(self) -> Bits1:
        return self != 0

    @property
    def P(self) -> Bits1:
        x = self._uint
        r = x & 1
        while (x := x >> 1) != 0:
            r ^= x & 1
        return _new_valid_bits(1, r)

    @property
    def Z(self) -> Bits1:
        return self == 0

    def ext(self, nbits: int) -> Bits:
        if not isinstance(nbits, int):
            raise TypeError("ext() argument must be an integer.")
        if nbits <= self._nbits:
            raise ValueError(
                "ext() argument must be greater than "
                f"the current width {self._nbits}."
            )
        value = _trunc_bits(int(self), nbits)
        return _new_valid_bits(nbits, value)

    # Type conversions
    #
    def __bool__(self) -> bool:
        return self._uint != 0

    def __int__(self) -> int:
        return self._uint

    def __index__(self) -> int:
        return self._uint

    def __hash__(self) -> int:
        all = (self._nbits, self._uint, self._next, self._last, self._mutable)
        return hash(all)

    # Representation
    #
    def __str__(self) -> str:
        width = (self._nbits - 1) // 4 + 1
        return f"{self._uint:X}".zfill(width)

    def __repr__(self) -> str:
        return f"Bits{self._nbits}(0x{self})"

    def bin(self) -> str:
        return f"0b{self.__bin()}"

    def __bin(self) -> str:
        return f"{self._uint:b}".zfill(self._nbits)

    def oct(self) -> str:
        width = (self._nbits - 1) // 3 + 1
        return "0o" + f"{self._uint:o}".zfill(width)

    def hex(self) -> str:
        return f"0x{self}"

    def pattern(self) -> str:
        return self.__bin()

    # State
    #
    def save(self):
        self._last = self._uint

    def flip(self):
        self._uint = self._next

    def changed(self) -> bool:
        return self._uint != self._last

    # Assignment
    # /=  : blocking assignment, assign to the current data
    # <<= : nonblocking assignment, assign to the next data
    #
    def __itruediv__(self, value: BitsData | ParamConst | int) -> Bits:
        n = self._nbits
        if not self._mutable:
            raise BitsAssignError(n, f"immutable Bits{n}")

        op = "assignment"  # for /= and @=
        if isinstance(value, ParamConst):
            value = value.param_value
        if isinstance(value, BitsData):
            value = value.data_bits
            if n != value._nbits:
                raise BitsWidthError(n, value._nbits, op)
            self._uint = value._uint
        elif isinstance(value, int):
            _check_nbits(n, value)
            self._uint = _trunc_bits(value, n)
        else:
            raise TypeError(f"Wrong RHS type {type(value)} for {op}.")
        return self

    def __ilshift__(self, value: BitsData | ParamConst | int) -> Bits:
        n = self._nbits
        if not self._mutable:
            raise BitsAssignError(n, f"immutable Bits{n}")

        op = "assignment"
        if isinstance(value, ParamConst):
            value = value.param_value
        if isinstance(value, BitsData):
            value = value.data_bits
            if n != value._nbits:
                raise BitsWidthError(n, value._nbits, op)
            self._next = value._uint
        elif isinstance(value, int):
            _check_nbits(n, value)
            self._next = _trunc_bits(value, n)
        else:
            raise TypeError(f"Wrong RHS type {type(value)} for {op}.")
        return self

    # Slice
    # `__getitem__` returns a new Bits.
    # `__setitem__` checks if immutable before setting.
    #
    def __getitem__(self, key: Any) -> Bits:
        if isinstance(key, (slice, tuple)):
            if isinstance(key, slice):
                start, stop = self.__get_slice_indices(key)
            else:
                start, stop = self.__get_part_select(key)
            k = stop - start
            mask = _bits_mask[k]
            value = (self._uint >> start) & mask
            return _new_valid_bits(k, value, self._mutable)

        idx = self.__get_index(key)
        value = (self._uint >> idx) & 1
        return _new_valid_bits(1, value, self._mutable)

    # Value cannot be a BitsData. Signal is not allowed in 'x[] = ...'.
    def __setitem__(self, key: Any, value: Bits | int):
        n = self._nbits
        if not self._mutable:
            raise BitsAssignError(n, f"slice of immutable Bits{n}")

        ov = int(self._uint)
        if isinstance(key, (slice, tuple)):
            if isinstance(key, slice):
                start, stop = self.__get_slice_indices(key)
            else:
                start, stop = self.__get_part_select(key)
            k = stop - start
            if isinstance(value, Bits):
                if k != value._nbits:
                    raise BitsWidthError(k, value._nbits, "slice assignment")
                nv = value._uint
            elif isinstance(value, int):
                nv = int(value)
                _check_nbits(k, nv)
            else:
                raise TypeError(
                    f"Wrong RHS type {type(value)} for slice assignment."
                )
            mask = _bits_mask[k]
            self._uint = (ov & ~(mask << start)) | ((nv & mask) << start)
            return

        idx = self.__get_index(key)
        if isinstance(value, Bits):
            if value._nbits > 1:
                raise ValueError(f"Value {value!r} is too wide for 1 bit.")
            nv = value._uint
        elif isinstance(value, int):
            nv = int(value)
            if nv != 0 and nv != 1:
                raise ValueError(f"Value {hex(nv)} is too wide for 1 bit.")
        else:
            raise TypeError(
                f"Wrong RHS type {type(value)} for indexed assignment."
            )
        self._uint = (ov & ~(1 << idx)) | ((nv & 1) << idx)

    def __get_slice_indices(self, key: slice) -> tuple[int, int]:
        n = self._nbits
        if key.step:
            raise IndexError("Bits index cannot contain step.")
        try:
            start = key.start.__index__() if key.start is not None else 0
            stop = key.stop.__index__() if key.stop is not None else n
            assert 0 <= start < stop <= n
        except AssertionError:
            if start < stop:
                raise IndexError(
                    f"Bits{n} index [{start},{stop}] is out of range."
                )
            else:
                raise IndexError(
                    f"Bits{n} index [{start},{stop}] is in wrong order."
                )
        return start, stop

    def __get_part_select(self, key: tuple) -> tuple[int, int]:
        if len(key) not in (2, 3):
            raise IndexError(
                "Part-select requires a tuple of (base, width[, ASC|DESC])."
            )

        # Base
        try:
            base = key[0].__index__()  # type: ignore
        except Exception as e:
            raise IndexError("Invalid part-select base.") from e

        # Width
        if isinstance(key[1], ParamConst):
            if not isinstance(key[1].param_value, int):
                raise IndexError(
                    "Part-select width must be an integer or Bits constant."
                )
            width = key[1].__index__()  # type: ignore
        elif isinstance(key[1], int):
            width = key[1]
        elif isinstance(key[1], Bits):
            assert not key[1].is_signed
            width = key[1].__index__()  # type: ignore
        else:
            raise IndexError(
                "Part-select width must be an integer or Bits constant."
            )

        # Direction
        if len(key) == 3:
            if not isinstance(key[2], Bits) or key[2].nbits != 1:
                raise IndexError(
                    "Part-select direction must be a Bits1 constant."
                )
            if key[2] == 1:
                if width < 0:
                    raise IndexError(
                        "Descending part-select cannot have negative width."
                    )
                width = -width

        # Check range
        n = self._nbits
        if not (base + width <= n and base + width + 1 >= 0):
            raise IndexError(f"Bits{n} part-select [{key}] is out of range.")
        if width == 0:
            raise IndexError("Part-select width cannot be 0.")
        if width > 0:
            start, stop = base, base + width
        else:
            stop, start = base + 1, base + width + 1  # (4, -4) -> [1:5]
        return start, stop

    def __get_index(self, key: Any) -> int:
        n = self._nbits
        idx = key.__index__()
        if idx < 0 or idx >= n:
            raise IndexError(f"Bits{n} index [{key}] is out of range.")
        return idx

    # Arithmetics
    # - Support (Bits __op__ BitsData|int), return a new Bits.
    # - ParamConst handles (ParamConst __op__ Bits).
    # - Call ParamConst's operator for (Bits __op__ ParamConst).
    #
    def __add__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__radd__(self)
        return self.__binary_op(other, lambda x, y: x + y, "+")

    def __radd__(self, other: Any) -> Bits | ParamConst:
        return self.__add__(other)

    def __sub__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__rsub__(self)
        return self.__binary_op(other, lambda x, y: x - y, "-")

    def __rsub__(self, other: Any) -> Bits | ParamConst:
        return self.__binary_op(other, lambda x, y: y - x, "-")

    def __mul__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__rmul__(self)
        return self.__binary_op(other, lambda x, y: x * y, "*")

    def __rmul__(self, other: Any) -> Bits | ParamConst:
        return self.__mul__(other)

    def __pos__(self) -> Bits:
        return self

    def __neg__(self) -> Bits:
        n = self._nbits
        return _new_valid_bits(n, _trunc_bits(-self._uint, n))

    # Bitwise operations
    # - Support (Bits __op__ BitsData|int), return a new Bits.
    # - ParamConst handles (ParamConst __op__ Bits).
    # - Call ParamConst's operator for (Bits __op__ ParamConst).
    #
    def __and__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__rand__(self)
        return self.__binary_op(other, lambda x, y: x & y, "&")

    def __rand__(self, other: Any) -> Bits | ParamConst:
        return self.__and__(other)

    def __or__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__ror__(self)
        return self.__binary_op(other, lambda x, y: x | y, "|")

    def __ror__(self, other: Any) -> Bits | ParamConst:
        return self.__or__(other)

    def __xor__(self, other: Any) -> Bits | ParamConst:
        if isinstance(other, ParamConst):
            return other.__rxor__(self)
        return self.__binary_op(other, lambda x, y: x ^ y, "^")

    def __rxor__(self, other: Any) -> Bits | ParamConst:
        return self.__xor__(other)

    def __binary_op(self, other: Any, op: Callable, op_name: str) -> Bits:
        n = self._nbits
        if isinstance(other, BitsData):
            other = other.data_bits
            if other.nbits != n:
                raise BitsWidthError(n, other.nbits, op_name)
            value = op(self._uint, other._uint) & _bits_mask[n]
            return _new_valid_bits(n, value)
        elif isinstance(other, int):
            other = int(other)
            try:
                _check_nbits(n, other)
            except ValueError as e:
                raise ValueError(f"Bits{n} {op_name}: {e}")
            value = op(self._uint, other) & _bits_mask[n]
            return _new_valid_bits(n, value)
        else:
            raise TypeError(f"Wrong type {type(other)} for {op_name}.")

    def __invert__(self) -> Bits:
        n = self._nbits
        return _new_valid_bits(n, _trunc_bits(~self._uint, n))

    # Shifts
    # Support (Bits __op__ BitsData|int), return a new Bits.
    # No limit on shift amount. Add a linter based on IR if necessary.
    #
    # No type hint for return value, avoiding to conflict with <<=
    def __lshift__(self, other: BitsData | int):
        return self.__shift_op(other, lambda x, y: x << y, "<<")

    def __rshift__(self, other: BitsData | int) -> Bits:
        return self.__shift_op(other, lambda x, y: x >> y, ">>")

    def __shift_op(
        self, other: BitsData | int, op: Callable, op_name: str
    ) -> Bits:
        n = self._nbits
        if isinstance(other, BitsData):
            if other.is_signed:
                raise ValueError("Signed shift amount is not supported.")
            other = other.data_bits
            value = op(int(self), other._uint) & _bits_mask[n]
            return _new_valid_bits(n, value)
        elif isinstance(other, int):
            other = int(other)
            if other < 0:
                raise ValueError("Signed shift amount is not supported.")
            value = op(int(self), other) & _bits_mask[n]
            return _new_valid_bits(n, value)
        else:
            raise TypeError(f"Wrong type {type(other)} for {op_name}.")

    # Comparisons
    # Support (Bits __op__ BitsData|int), return a new Bits1.
    #
    # About LHS/RHS:
    # Python tries comparison of LHS first, unless RHS is a subclass of LHS.
    #
    def __eq__(self, other: Any) -> Bits1:  # type: ignore
        return self.__eq_ne(other, lambda x, y: x == y, for_non_int=0)

    # Return a Bits, instead of a bool by `not __eq__()`.
    def __ne__(self, other: Any) -> Bits1:  # type: ignore
        return self.__eq_ne(other, lambda x, y: x != y, for_non_int=1)

    # No exception for wrong type. Just return unequal.
    def __eq_ne(self, other: Any, op: Callable, for_non_int: int) -> Bits1:
        n = self._nbits
        if isinstance(other, str):
            other = BitPat(other)
        if isinstance(other, BitsData):
            other = other.data_bits
            if other.nbits != n:
                raise BitsWidthError(other.nbits, n, "comparison")
            return _new_valid_bits(1, op(self._uint, other._uint))
        elif isinstance(other, BitPat):
            if other.nbits != n:
                raise BitsWidthError(n, other.nbits, "comparison")
            pat_uint = other.unsigned
            pat_mask = other.mask
            return _new_valid_bits(1, op(self._uint & pat_mask, pat_uint))
        elif isinstance(other, int):
            other = int(other)
            _check_nbits(n, other)
            return _new_valid_bits(1, op(int(self), other))
        else:
            return _new_valid_bits(1, for_non_int)

    def __lt__(self, other: Any) -> Bits1:
        return self.__compare(other, lambda x, y: x < y)

    def __le__(self, other: Any) -> Bits1:
        return self.__compare(other, lambda x, y: x <= y)

    def __gt__(self, other: Any) -> Bits1:
        return self.__compare(other, lambda x, y: x > y)

    def __ge__(self, other: Any) -> Bits1:
        return self.__compare(other, lambda x, y: x >= y)

    def __compare(self, other: Any, op: Callable) -> Bits1:
        n = self._nbits
        if isinstance(other, BitsData):
            other = other.data_bits
            if other.nbits != n:
                raise BitsWidthError(other.nbits, n, "comparison")
            return _new_valid_bits(1, op(int(self), int(other)))
        elif isinstance(other, int):
            other = int(other)
            _check_nbits(n, other)
            return _new_valid_bits(1, op(int(self), other))
        else:
            raise TypeError(f"Wrong type {type(other)} for Bits comparison.")

    # Replication
    def __pow__(self, count: int) -> SignalBundle:
        from comopy.hdl.signal_bundle import rep

        if not isinstance(count, int):
            raise TypeError(
                f"Replication count must be an integer, got {type(count)}."
            )
        if count < 0:
            raise ValueError("Replication count must be non-negative.")
        return rep(count, self)


class SignedBits(Bits):
    """Signed Bits."""

    @property
    def is_signed(self) -> bool:
        return True

    def __int__(self) -> int:
        return self.signed

    def __repr__(self) -> str:
        return f"SignedBits{self._nbits}(0x{self})"


# Bits1 for boolean type.
class Bits1(Bits):
    def __init__(self, *args, **kwargs):
        if hasattr(self, "_init_args"):
            # Called from Bits.__new__
            assert args[0] == 1
            args = self._init_args
        Bits.__init__(self, 1, *args, **kwargs)


# Convert any value to Bits1.
def Bool(value: Any) -> Bits1:
    if isinstance(value, BitsData):
        return value != 0
    else:
        return Bits1(bool(value))


# Register Bits1 in the type cache of Bits.
Bits._bits_types[1] = Bits1
