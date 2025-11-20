# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Build VSimulator wrapper and Python bindings for Verilated modules.
"""

from comopy.utils import PassGroup

from .binding_pass import BindingPass
from .compilation_pass import CompilationPass
from .translation_pass import TranslationPass


class BuildVSimulator(PassGroup):
    def __init__(self):
        super().__init__(TranslationPass(), BindingPass(), CompilationPass())
