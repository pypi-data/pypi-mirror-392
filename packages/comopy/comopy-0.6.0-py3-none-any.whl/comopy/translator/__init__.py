# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Translator for CIRCT IR generated from ComoPy HDL
"""

from .base_translator import BaseTranslator
from .setup_translator import SetupTranslator
from .translator_stage import TranslatorStage

__all__ = [
    # Translator interface
    "BaseTranslator",
    # Passes
    "SetupTranslator",
    # Stage
    "TranslatorStage",
]
