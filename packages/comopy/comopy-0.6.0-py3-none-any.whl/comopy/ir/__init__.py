# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Intermediate Representation (IR) for ComoPy HDL
"""

from .generate_ir import GenerateIR
from .ir_stage import IRStage

__all__ = [
    # Pass group
    "GenerateIR",
    # Stage
    "IRStage",
]
