# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Bit pattern.
"""


class BitPat:
    def __init__(self, pattern_str: str):
        assert isinstance(pattern_str, str)
        if not set(pattern_str).issubset({"0", "1", "?", "_"}):
            raise ValueError(f"Invalid bit pattern '{pattern_str}'.")
        self._pattern_str = pattern_str
        pattern = pattern_str.replace("_", "")
        if not pattern:
            raise ValueError("Empty bit pattern.")
        value = pattern.replace("?", "0")
        mask = pattern.replace("0", "1").replace("?", "0")
        self._pattern = pattern
        self._nbits = len(pattern)
        self._uint = int(value, 2)
        self._mask = int(mask, 2)

    # Properties
    #
    @property
    def nbits(self) -> int:
        return self._nbits

    @property
    def unsigned(self) -> int:
        return self._uint

    @property
    def mask(self) -> int:
        return self._mask

    # Representation
    #
    def __str__(self) -> str:
        return self._pattern_str

    def pattern(self) -> str:
        return self._pattern
