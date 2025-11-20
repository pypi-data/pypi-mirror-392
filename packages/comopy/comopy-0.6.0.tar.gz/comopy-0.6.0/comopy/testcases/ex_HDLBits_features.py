# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDLBits examples: more Verilog features.

See: https://hdlbits.01xz.net
"""

from comopy import *
from comopy import RawModule, build, comb  # for type checking


# Conditional ternary operator
class Conditional(RawModule):
    """https://hdlbits.01xz.net/wiki/Conditional"""

    @build
    def build_all(s):
        s.a = Input(8)
        s.b = Input(8)
        s.c = Input(8)
        s.d = Input(8)
        s.min = Output(8)

        s.m1 = Logic(8)
        s.m2 = Logic(8)
        s.m1 @= s.a if s.a < s.b else s.b
        s.m2 @= s.c if s.c < s.d else s.d
        s.min @= s.m1 if s.m1 < s.m2 else s.m2


# Reduction operators
class Reduction(RawModule):
    """https://hdlbits.01xz.net/wiki/Reduction"""

    @build
    def build_all(s):
        s.in_ = Input(8)
        s.parity = Output()
        s.parity @= s.in_.P


# Reduction: Even wider gates
class Gates100(RawModule):
    """https://hdlbits.01xz.net/wiki/Gates100"""

    @build
    def build_all(s):
        s.in_ = Input(100)
        s.out_and = Output()
        s.out_or = Output()
        s.out_xor = Output()

        s.out_and @= s.in_.AO
        s.out_or @= s.in_.NZ
        s.out_xor @= s.in_.P


# Combinational for-loop: Vector reversal 2
class Vector100r(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector100r"""

    @build
    def ports(s):
        s.in_ = Input(100)
        s.out = Output(100)

    @comb
    def update(s):
        for i in range(100):
            s.out[i] /= s.in_[100 - i - 1]


# Combinational for-loop: 255-bit population count
class Popcount255(RawModule):
    """https://hdlbits.01xz.net/wiki/Popcount255"""

    @build
    def ports(s):
        s.in_ = Input(255)
        s.out = Output(8)

    @comb
    def update(s):
        s.out /= 0
        for i in range(255):
            s.out /= s.out + s.in_[i].ext(8)


# Generate for-loop: 100-bit binary adder 2


# Generate for-loop: 100-digit BCD adder
