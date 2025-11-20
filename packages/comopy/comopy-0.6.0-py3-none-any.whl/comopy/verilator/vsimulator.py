# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Verilator-based simulator for executing verilated hardware models.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import comopy.hdl as HDL
from comopy.simulator.base_simulator import BaseSimulator


class VSimulator(BaseSimulator):

    _top_module: HDL.RawModule
    _extension_path: Path
    _verilated_module: ModuleType
    _vsimulator: Any  # VSimulator in the loaded extension
    _started: bool

    def __init__(self, top_module: HDL.RawModule, extension_path: Path):
        assert isinstance(top_module, HDL.RawModule) and top_module.assembled
        assert isinstance(extension_path, Path) and extension_path.is_file()
        self._top_module = top_module
        self._extension_path = extension_path
        self._verilated_module = self.__import_extension()
        self._vsimulator = self._verilated_module.VSimulator()
        self._started = False

    def __import_extension(self) -> ModuleType:
        ext_name = f"V{type(self._top_module).__name__}"
        spec = importlib.util.spec_from_file_location(
            ext_name, self._extension_path
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                f"Failed to load extension from: {self._extension_path}"
            )

        py_module = importlib.util.module_from_spec(spec)
        sys.modules[ext_name] = py_module
        spec.loader.exec_module(py_module)
        return py_module

    @property
    def module(self) -> HDL.RawModule:
        """Get the associated RawModule object."""
        return self._top_module

    @property
    def vsim_top(self) -> Any:
        """Get the top module instance in the verilated simulator."""
        if not self._started:
            raise RuntimeError(
                "Cannot access 'vsim_top' without starting the simulator."
            )
        return self._vsimulator.top

    def start(self):
        """Start simulation."""
        self._vsimulator.start()
        self._started = True

    def _init_all_module_ports(self):
        """Initialize all module ports. Internal use only for start()."""
        pass  # Not used

    def stop(self):
        """Stop simulation."""
        self._vsimulator.finish()
        self._started = False

    def evaluate(self) -> set[str]:
        """Evaluate the circuit and return the set of triggered signals."""
        self._vsimulator.eval()
        return set()

    def tick(self):
        """Run one clock cycle."""
        if not isinstance(self._top_module, HDL.Module):
            raise RuntimeError("tick() requires a Module with clock")

        top = self._vsimulator.top
        top.clk /= 0
        self._vsimulator.eval()
        top.clk /= 1
        self._vsimulator.eval()
