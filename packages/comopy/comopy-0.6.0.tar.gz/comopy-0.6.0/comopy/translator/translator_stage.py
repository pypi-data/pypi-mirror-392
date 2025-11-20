# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Translator stage: Installs translators into HDL modules.
"""

from typing import Any

from comopy.hdl import CircuitNode
from comopy.utils import BaseStage

from .setup_translator import SetupTranslator


class TranslatorStage(BaseStage):
    def __init__(self):
        super().__init__(SetupTranslator())

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
        if not input.ir_top:
            raise ValueError(
                f"{stage}: the circuit tree has not been processed by "
                "the IR stage."
            )
