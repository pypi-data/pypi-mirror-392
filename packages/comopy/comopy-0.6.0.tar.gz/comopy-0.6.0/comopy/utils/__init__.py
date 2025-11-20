# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Utility classes of ComoPy
"""

from .errors import (
    BitsAssignError,
    BitsWidthError,
    HDLAssemblyError,
    HDLSyntaxError,
)
from .func_code_info import CodePosition, FuncCodeInfo
from .str_match import match_lines
from .workflow import BasePass, BaseStage, JobPipeline, PassGroup

__all__ = [
    # Errors
    "BitsAssignError",
    "BitsWidthError",
    "HDLAssemblyError",
    "HDLSyntaxError",
    # Code information
    "CodePosition",
    "FuncCodeInfo",
    # Workflow
    "BasePass",
    "PassGroup",
    "BaseStage",
    "JobPipeline",
    # String matching
    "match_lines",
]
