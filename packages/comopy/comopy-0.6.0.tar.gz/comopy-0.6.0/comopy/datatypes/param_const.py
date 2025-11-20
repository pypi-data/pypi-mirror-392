# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Parameterized constant.

ParamConst describes a named constant used for HDL parameterization.
It also stores the expression tree that defines the constant.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Callable, Optional


class ParamConst:
    """Parameterized constant and its defining expression tree."""

    # Operators
    class Op(Enum):
        NOP = auto()
        ADD = auto()
        SUB = auto()
        MUL = auto()
        IDIV = auto()
        MOD = auto()
        AND = auto()
        OR = auto()
        XOR = auto()
        SHL = auto()
        SHR = auto()
        NEG = auto()
        INV = auto()
        ASSIGN = auto()

    # Name & value
    _param_name: str  # Avoid to conflict with CircuitObject._name
    _param_value: Any

    # Expression tree
    _op: ParamConst.Op
    _left: Optional[ParamConst | Any]  # ParamConst, literal value, or None
    _right: Optional[ParamConst | Any]  # ParamConst, literal value, or None

    # Iterator
    # NOTE: Simple iterator implementation with limitations:
    # - Iteration state is stored in instance, causing conflicts with
    #   nested/concurrent iterations
    # - Multiple iterations on the same object will interfere with each other
    # - Not thread-safe due to shared mutable state
    _it_queue: list[ParamConst]
    _it_index: int

    def __init__(self, value: Any, name: str = ""):
        if isinstance(value, ParamConst):
            value = value.param_value
        self._param_name = name
        self._param_value = value
        self._op = ParamConst.Op.NOP
        self._left = None
        self._right = None
        self._it_queue = []
        self._it_index = 0

    def alias(self) -> ParamConst:
        new = ParamConst(self.param_value)
        new._op = ParamConst.Op.ASSIGN
        new._left = self
        new._right = None
        return new

    # Properties
    #
    @property
    def param_name(self) -> str:
        return self._param_name

    @param_name.setter
    def param_name(self, name: str):
        self._param_name = name

    @property
    def param_value(self) -> Any:
        return self._param_value

    @property
    def op(self) -> ParamConst.Op:
        return self._op

    @property
    def left(self) -> Optional[ParamConst | Any]:
        return self._left

    @property
    def right(self) -> Optional[ParamConst | Any]:
        return self._right

    @property
    def is_expr(self) -> bool:
        return self._op != ParamConst.Op.NOP

    @property
    def is_literal(self) -> bool:
        return self._param_name == "" and not self.is_expr

    # Type conversions
    #
    def __index__(self) -> int:
        if isinstance(self._param_value, int):
            return self._param_value
        if hasattr(self._param_value, "__index__"):
            return self._param_value.__index__()
        raise TypeError(f"Cannot convert '{self._param_value}' to an index.")

    # Arithmetics
    #
    def __add__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x + y, ParamConst.Op.ADD)

    def __radd__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y + x, ParamConst.Op.ADD, reverse=True
        )

    def __sub__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x - y, ParamConst.Op.SUB)

    def __rsub__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y - x, ParamConst.Op.SUB, reverse=True
        )

    def __mul__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x * y, ParamConst.Op.MUL)

    def __rmul__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y * x, ParamConst.Op.MUL, reverse=True
        )

    def __neg__(self) -> ParamConst:
        return self.__unary_op(lambda x: -x, ParamConst.Op.NEG)

    # Bitwise operations
    #
    def __and__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x & y, ParamConst.Op.AND)

    def __rand__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y & x, ParamConst.Op.AND, reverse=True
        )

    def __or__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x | y, ParamConst.Op.OR)

    def __ror__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y | x, ParamConst.Op.OR, reverse=True
        )

    def __xor__(self, other: Any) -> ParamConst:
        return self.__binary_op(other, lambda x, y: x ^ y, ParamConst.Op.XOR)

    def __rxor__(self, other: Any) -> ParamConst:
        return self.__binary_op(
            other, lambda x, y: y ^ x, ParamConst.Op.XOR, reverse=True
        )

    def __invert__(self) -> ParamConst:
        return self.__unary_op(lambda x: ~x, ParamConst.Op.INV)

    def __binary_op(
        self,
        other: Any,
        func: Callable,
        op: ParamConst.Op,
        reverse: bool = False,
    ) -> ParamConst:
        if isinstance(other, ParamConst):
            other_value = other.param_value
        else:
            other_value = other
        result = ParamConst(func(self.param_value, other_value))
        result._op = op
        if reverse:
            result._left = other
            result._right = self
        else:
            result._left = self
            result._right = other
        return result

    def __unary_op(self, func: Callable, op: ParamConst.Op) -> ParamConst:
        result = ParamConst(func(self.param_value))
        result._op = op
        result._left = self
        result._right = None
        return result

    # Assignments
    # Disable all in-place assignments.
    #
    def __iadd__(self, other: Any):
        self.__wrong_assignment()

    def __isub__(self, other: Any):
        self.__wrong_assignment()

    def __imul__(self, other: Any):
        self.__wrong_assignment()

    def __imatmul__(self, other: Any):
        self.__wrong_assignment()

    def __itruediv__(self, other: Any):
        self.__wrong_assignment()

    def __ifloordiv__(self, other: Any):
        self.__wrong_assignment()

    def __imod__(self, other: Any):
        self.__wrong_assignment()

    def __ipow__(self, other: Any):
        self.__wrong_assignment()

    def __iand__(self, other: Any):
        self.__wrong_assignment()

    def __ior__(self, other: Any):
        self.__wrong_assignment()

    def __ixor__(self, other: Any):
        self.__wrong_assignment()

    def __ilshift__(self, other: Any):
        self.__wrong_assignment()

    def __irshift__(self, other: Any):
        self.__wrong_assignment()

    def __wrong_assignment(self):
        raise TypeError("Cannot assign to a ParamConst.")

    # Replace operand in an expression
    #
    def replace_operand(self, old: ParamConst, new: ParamConst):
        assert isinstance(old, ParamConst) and isinstance(new, ParamConst)
        assert old.param_value == new.param_value
        if self._left is old:
            self._left = new
        elif isinstance(self._left, ParamConst):
            self._left.replace_operand(old, new)
        if self._right is old:
            self._right = new
        elif isinstance(self._right, ParamConst):
            self._right.replace_operand(old, new)

    # Iterator
    # NOTE: This simple iterator implementation has design flaws:
    # - Resets state on each __iter__ call, breaking nested iterations.
    # - Instance acts as both iterable and iterator, violating separation
    #   of concerns.
    #
    def __iter__(self):
        self._it_queue = [self]
        self._it_index = 0
        return self

    def __next__(self) -> ParamConst:
        # Breadth-first traversal of expression tree
        # LIMITATION: Modifies shared instance state during iteration
        if self._it_index >= len(self._it_queue):
            self._it_queue = []
            self._it_index = 0
            raise StopIteration
        node = self._it_queue[self._it_index]
        self._it_index += 1
        if isinstance(node, ParamConst):
            if node.left:
                self._it_queue.append(node.left)
            if node.right:
                self._it_queue.append(node.right)
        return node
