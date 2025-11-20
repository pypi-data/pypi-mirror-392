# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Base class for all circuit objects.
"""

from enum import Enum
from typing import Any, Optional


class IODirection(Enum):
    In = 0
    Out = 1
    InOut = 2  # bidirectional IOStruct

    @classmethod
    def flip(cls, direction):
        if direction == cls.In:
            return cls.Out
        else:
            assert direction == cls.Out
            return cls.In


class CircuitObject:
    """Base class for all circuit objects.

    Each circuit object is named after its corresponding variable name,
    which is set by AssembleHDL. Specify the name of the top module using
    the 'name=...' argument during initialization.
    """

    _name: str
    _node: Any  # CircuitNode, avoid circular import
    _assembled: bool
    _simulating: bool

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._name = kwargs.pop("name", "")
        obj._node = None
        obj._assembled = False
        obj._simulating = False
        obj._args = args
        obj._kwargs = kwargs
        return obj

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    # Properties
    #
    @property
    def name(self) -> str:
        return self._name if self._name else "_Unknown_"

    @property
    def node(self) -> Any:
        return self._node

    @property
    def assembled(self) -> bool:
        return self._assembled

    @property
    def simulating(self) -> bool:
        return self._simulating

    @simulating.setter
    def simulating(self, value: bool):
        assert self._assembled
        self._simulating = value

    @property
    def is_module(self) -> bool:
        return False

    @property
    def is_package(self) -> bool:
        return False

    @property
    def direction(self) -> Optional[IODirection]:
        return None

    @property
    def is_input_port(self) -> bool:
        return False

    @property
    def is_output_port(self) -> bool:
        return False

    @property
    def is_inout_port(self) -> bool:
        return self.is_input_port and self.is_output_port

    @property
    def is_port(self) -> bool:
        return self.is_input_port or self.is_output_port

    @property
    def is_scalar_input(self) -> bool:
        return False

    # Assembling
    #
    def _assemble(self):
        if not self._assembled:
            self.assemble()
            self._assembled = True

    def assemble(self):
        """Assemble the circuit object."""
