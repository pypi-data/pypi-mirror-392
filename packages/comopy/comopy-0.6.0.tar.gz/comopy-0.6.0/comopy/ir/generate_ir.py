# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Generate IR from an assembled HDL circuit tree.
"""

from comopy.utils import PassGroup

from .behavior_pass import BehaviorPass
from .structure_pass import StructurePass


class GenerateIR(PassGroup):
    def __init__(self):
        super().__init__(StructurePass(), BehaviorPass())
