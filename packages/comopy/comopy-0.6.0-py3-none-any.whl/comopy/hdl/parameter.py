# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Local and module parameters.

LocalParam and ModuleParam correspond to local parameters and module
parameters in SystemVerilog.
"""

from __future__ import annotations

from typing import Any

from comopy.datatypes import Bits, ParamConst

from .circuit_object import CircuitObject


class ModuleParam(ParamConst):
    """Module parameter."""


class LocalParam(ParamConst, CircuitObject):
    """Local parameter for defining constants in modules and packages."""

    _pkg_name: str = ""  # Name of the owning package, for use_package()

    def __init__(self, value: Any):
        CircuitObject.__init__(self)

        # Literal constant
        if isinstance(value, (int, Bits)):
            ParamConst.__init__(self, value)
            return

        # Assign from an assembled LocalParam or a module parameter
        if isinstance(value, (LocalParam, ModuleParam)):
            assert value.param_name
            ParamConst.__init__(self, value.param_value)
            self._op = ParamConst.Op.ASSIGN
            self._left = value
            self._right = None
            return

        if isinstance(value, ParamConst):
            # Create a LocalParam from a ParamConst expression
            assert value.param_name == "" and value.is_expr
            if not self.__is_const_expr(value):
                raise ValueError(
                    "Invalid expression for LocalParam."
                    "\n- Not a constant expression or unsupported data type?"
                )
            ParamConst.__init__(self, value.param_value)
            self._op = value._op
            self._left = value._left
            self._right = value._right
            return

        raise TypeError(f"Invalid data type for LocalParam: {type(value)}")

    def __is_const_expr(self, value: ParamConst) -> bool:
        for node in value:
            if isinstance(node, (LocalParam, ModuleParam)):
                assert node.param_name
            elif isinstance(node, ParamConst):
                assert node.param_name == "" and node.is_expr
            elif not isinstance(node, (int, Bits)):
                return False
        return True

    def alias(self) -> LocalParam:
        assert isinstance(self.param_value, (int, Bits))
        new = LocalParam(self.param_value)
        new._op = ParamConst.Op.ASSIGN
        new._left = self
        new._right = None
        return new

    def clone(self) -> LocalParam:
        assert isinstance(self.param_value, (int, Bits))
        new = LocalParam(self.param_value)
        new._op = self._op
        new._left = self._left
        new._right = self._right
        return new

    @property
    def pkg_name(self) -> str:
        return self._pkg_name

    @pkg_name.setter
    def pkg_name(self, name: str):
        self._pkg_name = name

    # Assembling
    #
    def assemble(self):
        assert self._name and self._param_name == ""
        self.param_name = self._name
