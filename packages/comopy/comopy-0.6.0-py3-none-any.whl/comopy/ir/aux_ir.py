# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Auxiliary IR elements for AST-to-IR translation.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Sequence

import circt.ir as IR
from circt.dialects import sv


# Forced CIRCT i32 for integer expressions
#
class ForcedI32Type(Enum):
    """Enumeration for forced i32 type usage."""

    FUNCTION_RET = auto()
    LOCAL_PARAM = auto()
    LOOP_VAR = auto()
    CONSTANT_EXPR = auto()
    VARIABLE_EXPR = auto()


# Bits
#
class NotBits:
    """A not-Bits expression, such as Signal, SignalSlice, etc."""

    pass


@dataclass(frozen=True)
class SignedValue:
    """A signed IR.Value, as returned by Bits.S."""

    bits_ir: IR.Value


@dataclass(frozen=True)
class BitsMethod:
    """A bound Bits method with associated IR.Value and method name."""

    method_name: str
    bits_ir: SignedValue | IR.Value


# Concatenation
#
class ConcatLHS:
    """A concatenation for left-hand side usage.

    CIRCT core IR does not directly support left-hand side concatenation
    assignments, requiring conversion to assignments of individual parts.
    Therefore, ConcatLHS records the composition when parsing left-hand side
    concatenations.
    """

    def __init__(self, parts: Sequence[Any]):
        # Import here to avoid circular dependency
        from .circt_ir import ir_width

        # Store (part, width) tuples in the part list
        self._parts = []
        self._width = 0
        for part in parts:
            if isinstance(part, sv.LogicOp):
                part_width = ir_width(part)
            elif isinstance(part, IR.OpResult):
                # sv.IndexedPartSelectInOut
                part_width = ir_width(part)
            elif isinstance(part, ConcatLHS):
                part_width = part.width
            else:
                raise TypeError(f"Unsupported part type: {type(part)}")
            self._parts.append((part, part_width))
            self._width += part_width

    @property
    def width(self) -> int:
        return self._width

    @property
    def parts(self) -> list[tuple[Any, int]]:
        return self._parts


# For statement
#
@dataclass(frozen=True)
class LoopVar:
    """An induction variable in a for loop."""

    name: str
    var: IR.BlockArgument


@dataclass(frozen=True)
class LoopRange:
    """A loop range with start, stop, step values."""

    start: int
    stop: int
    step: int


# Match statement
#
@dataclass
class CaseDefault:
    """A default case in a match statement."""

    explicit_empty: bool = False  # True if body explicitly uses 'pass'
