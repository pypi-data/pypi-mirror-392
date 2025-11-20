# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Circuit objects for signal, logic, port and etc.
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

from comopy.datatypes import Bits, ParamConst

from .circuit_object import CircuitObject, IODirection
from .connectable import Connectable
from .signal_slice import SignalSlice

if TYPE_CHECKING:
    from .signal_array import SignalArray


# Decorator for simulation-time APIs
def simulation(func: Callable) -> Callable:
    @wraps(func)
    def _checked_func(self, *args, **kwargs):
        if not self.simulating:
            func_name = f"{self.__class__.__name__}.{func.__name__}()"
            raise RuntimeError(f"{func_name} is a simulation-time API.")
        return func(self, *args, **kwargs)

    return _checked_func


class Signal(Connectable, CircuitObject):

    # Instance attributes
    _nbits: int
    _width_param: ParamConst
    _direction: Optional[IODirection]
    _link: Optional[Connectable]
    _data_type: Type[Bits]
    _data: Bits
    _data_dry_run: Bits
    _data_driven: Bits

    # Construction
    #
    def __init__(
        self, width: int | ParamConst = 1, link: Optional[Connectable] = None
    ):
        CircuitObject.__init__(self)

        # Setup width and width parameter
        if isinstance(width, ParamConst):
            width_param = width
            if not isinstance(width.param_value, int):
                raise TypeError(
                    "Integer is expected for parameterized width of Signal."
                )
            if not self.__is_param_expr(width):
                raise ValueError(
                    "Invalid expression for parameterized width of Signal."
                    "\n- Only expressions containing LocalParam, ModuleParam "
                    "and integers are allowed."
                )
            width = width.param_value
        else:
            width_param = ParamConst(width)
        assert isinstance(width, int)
        self._nbits = width
        # Avoid assembling LocalParam for width_param
        object.__setattr__(self, "_width_param", width_param)

        # Setup data
        self._direction = None
        self._data_type = type(Bits(width))
        self._data_dry_run = Bits(width, 0, mutable=True)
        if isinstance(link, Connectable):
            if self._nbits != link.nbits:
                raise ValueError("Incompatible bit width for Signal link.")
            # Support linking an assembled signal during the assembly process.
            # For example, create an inner structure while assembling a union.
            object.__setattr__(self, "_link", link)
        else:
            self._link = None
            self._data = Bits(width, 0, mutable=True)
            self._data_driven = Bits(width, 0, mutable=True)

    def __is_param_expr(self, value: ParamConst) -> bool:
        assert False, "UNIMPLEMENTED"

    def input(self):
        assert not self.assembled
        if self._direction is not None:
            raise RuntimeError("Cannot change signal direction.")
        self._direction = IODirection.In
        return self

    def output(self):
        assert not self.assembled
        if self._direction is not None:
            raise RuntimeError("Cannot change signal direction.")
        self._direction = IODirection.Out
        return self

    # Ensure 'flipped' is a keyword-only argument to prevent misuse as 'link'.
    def create(
        self, link: Connectable | None = None, *, flipped: bool = False
    ) -> Signal:
        """Create a new instance of the same type."""
        cls = self.__class__
        if self._width_param.is_literal:
            assert isinstance(self._width_param.param_value, int)
            new = cls(self._width_param.param_value, link)
        else:
            new = cls(self._width_param, link)
        if self._direction is not None:
            if flipped:
                new._direction = IODirection.flip(self._direction)
            else:
                new._direction = self._direction
        return new

    # Signal @ count -> SignalArray
    def __matmul__(self, count: int) -> SignalArray:
        from .signal_array import SignalArray

        if not isinstance(count, int):
            raise TypeError(
                f"Array size must be an integer, got {type(count)}."
            )
        if count <= 0:
            raise ValueError("Array size must be positive.")
        return SignalArray(self, count)

    # BitsData
    #
    @property
    def data_bits(self) -> Bits:
        from .assemble_hdl import AssembleHDL

        if AssembleHDL.is_assembling():
            # Dry run to check data type before connecting
            return self._data_dry_run
        return self.data_sim()

    @simulation
    def data_sim(self) -> Bits:
        if self._link is None:  # Avoid __bool__()
            return self._data
        else:
            return self._link.data_bits

    @property
    def nbits(self) -> int:
        return self._nbits

    # Connectable
    #
    @property
    def data_driven(self) -> Bits:
        if self._link is None:  # Avoid __bool__()
            return self._data_driven
        else:
            return self._link.data_driven

    @data_driven.setter
    def data_driven(self, value: Bits | int):
        assert isinstance(value, (Bits, int))
        if self._link is None:  # Avoid __bool__()
            self._data_driven /= value
        else:
            self._link.data_driven = value  # type: ignore

    # CircuitObject
    #
    @property
    def direction(self) -> Optional[IODirection]:
        return self._direction

    @property
    def is_input_port(self) -> bool:
        return self.direction == IODirection.In

    @property
    def is_output_port(self) -> bool:
        return self.direction == IODirection.Out

    @property
    def is_scalar_input(self) -> bool:
        return self.is_input_port and self._nbits == 1

    # Properties
    #
    @property
    def data_type(self) -> Type[Bits]:
        return self._data_type

    @property
    def width_param(self) -> ParamConst:
        return self._width_param

    # Type conversion
    #
    def __bool__(self) -> bool:
        if not self.simulating:
            return True  # self is not None
        return bool(self.data_bits)

    def __str__(self) -> str:
        if self._link is not None:  # Avoid __bool__()
            return str(self._link)
        cls_name = self.__class__.__name__
        return f"{cls_name}{{{self._data!r}}}"

    # State
    #
    @simulation
    def save(self):
        assert self._link is None  # Avoid __bool__()
        self._data.save()

    @simulation
    def flip(self):
        assert self._link is None  # Avoid __bool__()
        self._data.flip()

    @simulation
    def changed(self) -> bool:
        assert self._link is None  # Avoid __bool__()
        return self._data.changed()

    # Assignment
    #
    # /= : blocking assignment
    def __itruediv__(self, value: Any) -> Signal:
        if not self.simulating:
            raise RuntimeError(
                "/= (blocking assignment) is a simulation-time API."
            )
        if self._link is None:  # Avoid __bool__()
            self._data /= value
        else:
            self._link /= value
        return self

    # <<= : nonblocking assignment
    def __ilshift__(self, value: Any) -> Signal:
        if not self.simulating:
            raise RuntimeError(
                "<<= (nonblocking assignment) is a simulation-time API."
            )
        if self._link is None:  # Avoid __bool__()
            self._data <<= value
        else:
            self._link <<= value
        return self

    # @= : continuous assignment (connection)
    # Use Connectable.@=()

    # Slice
    #
    def __getitem__(self, key: Any) -> SignalSlice:
        return SignalSlice(self, key)

    # In-place assignment to a slice ultimately calls `__setitem__`.
    # E.g. `a[2:] /= 1` => `slice = a[2:], res = slice./=(1), a[2:] = res`
    # Allow setting the same item of a SignalSlice to support `a[] /= ...`.
    # Reject other slice assignments. `a[] =...`, `a[] +=...` are illegal.
    # Exception: `t = a[2:], ..., a[2:] = t` is legal. We can't distinguish
    # it from `a[2:] /=...` without inspecting the Python code. Fortunately,
    # it is harmless. Maybe we can check this case in IR?
    def __setitem__(self, key: Any, value: SignalSlice):
        if isinstance(value, SignalSlice):
            if value._owner is self and value._key == key:
                # Assignment has been done in `__itruediv__`, `__imatmul__`
                return
        super().__setitem__(key, value)


class Wire(Signal):
    """SystemVerilog 'wire', allows multiple continuous drivers"""

    # Multi-drive support is not implemented yet.


class Logic(Signal):
    """SystemVerilog 'logic'"""


# I/O Port
# Input and Output are shortcuts for Wire().input() and Wire().output().
# I/O ports cannot be used in PackagedStruct/Union, and therefore do not
# support 'link' argument.
# NOTE: In CIRCT, ports only support 'wire' type, instead of 'logic'.
def Input(Type: int | ParamConst = 1) -> Wire:
    return Wire(Type).input()


def Output(Type: int | ParamConst = 1) -> Wire:
    return Wire(Type).output()
