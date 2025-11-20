# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
IR stage configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IRConfig:
    comment_lhs_concat: bool = True
    comment_lhs_slice: bool = False
    comment_bits_folding: bool = False
    comment_instance: bool = False

    @staticmethod
    def debug() -> IRConfig:
        return IRConfig(
            comment_lhs_concat=True,
            comment_lhs_slice=True,
            comment_bits_folding=True,
            comment_instance=True,
        )
