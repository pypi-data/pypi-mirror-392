# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Predefined subclasses of Bits.

- Bits<N>: Type aliases for N-bit vector types (e.g., Bits8 for 8 bits).
- b<N>: Type aliases for N-bit literal constants (e.g., b8 for 8-bit literals).
"""

from typing import TypeAlias

from .bits import Bits, Bits1, _bits_nmax

# Boolean constants
FALSE = Bits1(0)
TRUE = Bits1(1)

# Part-select directions
ASC = Bits1(0)
DESC = Bits1(1)

# Define additional Bits types in the global namespace of this module.
b1: TypeAlias = Bits1
for n in range(2, _bits_nmax + 1):
    globals()[f"Bits{n}"] = globals()[f"b{n}"] = type(Bits(n))

# All Bits types to be exported
_all_BitsN = [f"Bits{n}" for n in range(1, _bits_nmax + 1)]
_all_bitsN = [f"b{n}" for n in range(1, _bits_nmax + 1)]
