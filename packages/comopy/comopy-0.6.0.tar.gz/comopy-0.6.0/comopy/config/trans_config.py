# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Translator stage configuration.
"""

from dataclasses import dataclass


@dataclass
class TranslatorConfig:

    dest_dir: str = ""  # Default: <top_module_dir>/build/
