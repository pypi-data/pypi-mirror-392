# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDL module classes with implicit signal support.
"""

from .raw_module import RawModule


class ClockModule(RawModule):
    """Base class for HDL modules providing an implicit clock."""

    # Class attributes
    _auto_pos_edges = ("clk",)


# Module is an alias for ClockModule, covering the most common case
Module = ClockModule
