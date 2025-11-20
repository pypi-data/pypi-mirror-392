# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Hardware Description Language (HDL) of ComoPy
"""

from .assemble_hdl import AssembleHDL
from .circuit_node import (
    Behavior,
    CircuitNode,
    Connection,
    Dependency,
    ModuleInst,
    Sensitivity,
)
from .circuit_object import CircuitObject, IODirection
from .connectable import Connectable
from .hdl_stage import HDLStage
from .io_struct import IOStruct
from .module import ClockModule, Module
from .raw_module import RawModule, build, comb, seq
from .signal import Input, Logic, Output, Signal, Wire
from .signal_array import SignalArray
from .signal_bundle import SignalBundle, cat, rep
from .signal_slice import SignalSlice

__all__ = [
    # Circuit object & tree node
    "CircuitObject",
    "CircuitNode",
    "Behavior",
    "ModuleInst",
    "Connection",
    "Dependency",
    "Sensitivity",
    # Module & package
    "RawModule",
    "ClockModule",
    "Module",
    "build",
    "comb",
    "seq",
    # Signal
    "Connectable",
    "IODirection",
    "Signal",
    "Wire",
    "Logic",
    "Input",
    "Output",
    "SignalArray",
    "SignalBundle",
    "SignalSlice",
    "IOStruct",
    "cat",
    "rep",
    # Stage
    "AssembleHDL",
    "HDLStage",
]
