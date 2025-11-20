# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang


"""
HDL stage: Assembles all HDL objects.
"""

from typing import Any

from comopy.utils import BaseStage

from .assemble_hdl import AssembleHDL
from .package import Package
from .raw_module import RawModule


class HDLStage(BaseStage):
    def __init__(self):
        super().__init__(AssembleHDL())

    def check_input(self, input: Any):
        if not isinstance(input, (RawModule, Package)):
            raise TypeError(f"{self.name} expects an HDL module or package.")
