# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Unpacked array of Signal objects.
"""

from __future__ import annotations

from typing import Any

from comopy.datatypes import BitsData

from .circuit_object import CircuitObject
from .signal import Signal


class SignalArray(CircuitObject):
    """Unpacked array of Signal objects."""

    _size: int
    _elem_template: Signal
    _elements: list[Signal]
    _dirty_entries: set[int]

    def __init__(self, element: Signal, size: int):
        if not isinstance(element, Signal):
            raise ValueError(
                "Template element of SignalArray should be a Signal object."
            )
        if element.assembled:
            raise ValueError(
                "Template element of SignalArray cannot be assembled."
            )
        if element.direction:
            raise ValueError(
                "Template element of SignalArray cannot be a port."
            )
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Array size should be a positive integer.")

        super().__init__()
        self._size = size
        self._elements = [element.create() for _ in range(size)]
        self._dirty_entries = set()
        # Avoid assembling the template element
        object.__setattr__(self, "_elem_template", element)

    # CircuitObject
    #
    @property
    def simulating(self) -> bool:
        if self._simulating:
            assert self._assembled
        return self._simulating

    @simulating.setter
    def simulating(self, value: bool):
        assert self._assembled
        self._simulating = value
        for elem in self._elements:
            assert elem._assembled
            elem.simulating = value

    # Properties
    #
    @property
    def size(self) -> int:
        return self._size

    @property
    def elem_template(self) -> Signal:
        return self._elem_template

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        assert isinstance(self._elem_template, Signal)
        elem_cls = self._elem_template.__class__.__name__
        signal = f"{elem_cls}{{Bits{self._elem_template.nbits}}}"
        return f"{signal}[{self._size}]"

    # Assembling
    #
    def assemble(self):
        for elem in self._elements:
            elem._assemble()

    # State
    #
    def save(self):
        # No saved state for array elements
        pass

    def flip(self):
        for index in self._dirty_entries:
            self._elements[index].flip()
        self._dirty_entries.clear()

    def changed(self) -> bool:
        # Always trigger array elements
        return True

    # Item access
    #
    def __getitem__(self, key: Any) -> Signal:
        if isinstance(key, slice):
            raise IndexError(f"{self} is not sliceable.")
        if isinstance(key, tuple):
            raise IndexError(f"{self} is not part-selectable.")
        if not isinstance(key, (int, BitsData)):
            raise IndexError(f"Index of {self} should be an integer or Bits.")
        index = int(key)
        if index < 0 or index >= self._size:
            raise IndexError("Array index is out of range.")
        # Mark the element as dirty.
        # The returned item may be modified in a slice or bundle later, which
        # does not reach SignalArray.__setitem__().
        self._dirty_entries.add(index)
        return self._elements[key]

    def __setitem__(self, key: Any, value: Signal):
        if isinstance(key, slice):
            raise IndexError(f"{self} is not sliceable.")
        if isinstance(key, tuple):
            raise IndexError(f"{self} is not part-selectable.")
        if not isinstance(key, (int, BitsData)):
            raise IndexError(f"Index of {self} should be an integer or Bits.")
        index = int(key)
        assert index >= 0 and index < self._size
        if self._elements[index] is not value:
            raise ValueError(
                "Wrong assignment type."
                "\n- Use /= (blocking assignment) "
                "or <<= (nonblocking assignment)."
            )

    # Memory interface
    #
    def read_mem(self, mem: list):
        if not isinstance(mem, list):
            raise ValueError("Memory data should be a list.")
        size = min(len(mem), self._size)
        for i in range(size):
            elem = self._elements[i]
            assert isinstance(elem, Signal)
            elem._data /= mem[i]
            elem._data <<= mem[i]
