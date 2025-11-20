# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Verilator stage: Build verilator simulator from an HDL circuit tree.
"""

from typing import Any

from comopy.hdl import CircuitNode, RawModule
from comopy.utils import BaseStage

from .build_vsimulator import BuildVSimulator


class VerilatorStage(BaseStage):
    def __init__(self):
        super().__init__(BuildVSimulator())

    def check_input(self, input: Any):
        stage = self.name
        if not isinstance(input, CircuitNode):
            raise TypeError(
                f"{stage}: input must be an HDL.CircuitNode "
                "(the root of a circuit tree)."
            )
        if not input.is_root:
            raise ValueError(
                f"{stage}: input must be the root of a circuit tree."
            )

        top = input.obj
        assert isinstance(top, RawModule)
        if not top.translator:
            raise ValueError(
                f"{stage}: the circuit tree has not been processed by "
                "the translator stage."
            )
