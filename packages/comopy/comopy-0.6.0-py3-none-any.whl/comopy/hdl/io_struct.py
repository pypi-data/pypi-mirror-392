# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Structured I/O interface for module ports.

IOStruct organizes directional module ports into a hierarchical interface.
It enables the definition of grouped and named ports, which can be mapped to
SystemVerilog 'interface' and 'modport' constructs for improved code clarity
and reuse.
"""

from .circuit_object import CircuitObject, IODirection
from .raw_module import RawModule
from .signal import Signal


class IOStruct(CircuitObject):
    """
    Structured I/O interface for module ports.

    IOStruct creates and assembles its instance members from circuit objects
    declared as class attributes. These class attributes serve as templates
    for the I/O interface, enabling hierarchical grouping, reuse, and easier
    testing of module ports.
    """

    _part_names: list[str]
    _has_input: bool
    _has_output: bool

    def __init__(self):
        cls = self.__class__
        self._part_names = []
        self._has_input = False
        self._has_output = False
        for name, obj in vars(cls).items():
            if not isinstance(obj, (Signal, IOStruct)):
                continue
            if hasattr(IOStruct, name):
                raise ValueError(
                    f"Cannot overwrite attribute '{name}' of IOStruct."
                )
            if obj.direction is None:
                raise ValueError(
                    f"Non-directional member '{name}' in "
                    f"I/O structure '{cls.__name__}'."
                    "\n- In-out ports are not supported. "
                    "Use PackedStruct to organize non-directional signals."
                    "\n- Use port() or flipped() to specify direction "
                    "for nested IOStruct members."
                )
            if obj.direction == IODirection.In:
                self._has_input = True
            elif obj.direction == IODirection.Out:
                self._has_output = True
            else:
                assert obj.direction == IODirection.InOut
                self._has_input = True
                self._has_output = True
            self._part_names.append(name)
        if not self._part_names:
            raise ValueError(f"Empty I/O structure '{cls.__name__}'.")
        super().__init__()

    def __get_template_part(self, name: str) -> Signal:
        obj = getattr(self.__class__, name, None)
        assert isinstance(obj, Signal)
        return obj

    # I/O template for unit tests
    #
    def match_module_io(self, module: RawModule) -> bool:
        assert not self.assembled
        for name in self._part_names:
            obj = self.__get_template_part(name)
            if not hasattr(module, name):
                return False
            obj_in_module = getattr(module, name, None)
            if not isinstance(obj_in_module, Signal):
                return False
            if obj.nbits != obj_in_module.nbits:
                return False
            if obj.direction != obj_in_module.direction:
                return False
        return True

    def match_data(self, data: tuple) -> bool:
        assert not self.assembled
        if len(data) != len(self._part_names):
            return False
        for i, name in enumerate(self._part_names):
            if data[i] is None:
                continue
            obj = self.__get_template_part(name)
            try:
                obj.data_type(data[i])
            except Exception:
                return False
        return True

    def assign_inputs(self, module: RawModule, data: tuple):
        assert not self.assembled
        assert len(data) == len(self._part_names)
        for i, name in enumerate(self._part_names):
            obj = self.__get_template_part(name)
            if obj.direction != IODirection.In:
                continue
            if (value := data[i]) is None:
                continue
            signal = getattr(module, name, None)
            assert isinstance(signal, Signal)
            signal /= value

    def verify_outputs(self, module: RawModule, data: tuple):
        assert not self.assembled
        assert len(data) == len(self._part_names)
        for i, name in enumerate(self._part_names):
            obj = self.__get_template_part(name)
            if obj.direction != IODirection.Out:
                continue
            if (value := data[i]) is None:
                continue
            signal = getattr(module, name, None)
            assert isinstance(signal, Signal)
            # Compare in the same width
            if isinstance(value, int):
                bits = signal.data_type(value)
            else:
                bits = value
            if signal != bits:
                raise ValueError(
                    f"{module}.{name}({signal.data_bits.hex()}) != {value:#x}"
                )
