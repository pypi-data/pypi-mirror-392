# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
ComoPy: Co-modeling tools for hardware generation with Python
"""

__version__ = "0.6.0"

from .bits import *
from .bits import ASC, DESC, FALSE, TRUE, _all_BitsN, _all_bitsN
from .config import (
    ComopyContext,
    IRConfig,
    SimulatorConfig,
    TranslatorConfig,
    comopy_context,
    get_comopy_context,
    set_comopy_context,
)
from .datatypes import (
    Bits,
    Bool,
)
from .hdl import (
    HDLStage,
    Input,
    IOStruct,
    Logic,
    Module,
    Output,
    RawModule,
    build,
    cat,
    comb,
    rep,
    seq,
)
from .ir import IRStage
from .simulator import BaseSimulator, SimulatorStage
from .testcases import BaseTestCase
from .translator import TranslatorStage
from .utils import (
    BitsAssignError,
    BitsWidthError,
    HDLAssemblyError,
    HDLSyntaxError,
    JobPipeline,
)
from .verilator import VerilatorStage

__all__ = (
    [
        # Bits constants
        "TRUE",
        "FALSE",
        "ASC",
        "DESC",
        # Data types
        "Bits",
        "Bool",
        # Errors
        "BitsAssignError",
        "BitsWidthError",
        "HDLAssemblyError",
        "HDLSyntaxError",
        # HDL
        "RawModule",
        "Module",
        "Logic",
        "Input",
        "Output",
        "IOStruct",
        "build",
        "comb",
        "seq",
        "cat",
        "rep",
        # Simulator
        "BaseSimulator",
        # Workflow
        "HDLStage",
        "IRStage",
        "SimulatorStage",
        "TranslatorStage",
        "VerilatorStage",
        "JobPipeline",
        # Configuration
        "ComopyContext",
        "IRConfig",
        "SimulatorConfig",
        "TranslatorConfig",
        "comopy_context",
        "get_comopy_context",
        "set_comopy_context",
        # Testing
        "BaseTestCase",
    ]
    + _all_BitsN
    + _all_bitsN
)
