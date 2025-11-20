# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDLBits examples: basics and vectors using continuous assignments (@=).

See: https://hdlbits.01xz.net
"""

from comopy import *
from comopy import RawModule, build  # for type checking

#
# Replace 'in_' in translated Verilog to 'in' before submitting to HDLBits.
#


# Basics
#

# Simple wire
# Input, Output, @=
class Wire1(RawModule):
    """https://hdlbits.01xz.net/wiki/Wire"""

    @build
    def ports(s):
        s.in_ = Input()
        s.out = Output()

    @build
    def connect(s):
        s.out @= s.in_


# Four wires
# Input, Output, @=
class Wire4(RawModule):
    """https://hdlbits.01xz.net/wiki/Wire4"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.c = Input()
        s.w = Output()
        s.x = Output()
        s.y = Output()
        s.z = Output()

    @build
    def connect(s):
        s.w @= s.a
        s.x @= s.b
        s.y @= s.b
        s.z @= s.c


# Inverter
# ~
class Notgate(RawModule):
    """https://hdlbits.01xz.net/wiki/Notgate"""

    @build
    def ports(s):
        s.in_ = Input()
        s.out = Output()

    @build
    def connect(s):
        s.out @= ~s.in_


# AND gate
# &
class Andgate(RawModule):
    """https://hdlbits.01xz.net/wiki/Andgate"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.out = Output()

    @build
    def connect(s):
        s.out @= s.a & s.b


# NOR gate
# ~, |
class Norgate(RawModule):
    """https://hdlbits.01xz.net/wiki/Norgate"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.out = Output()

    @build
    def connect(s):
        s.out @= ~(s.a | s.b)


# XNOR gate
# ~, ^
class Xnorgate(RawModule):
    """https://hdlbits.01xz.net/wiki/Xnorgate"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.out = Output()

    @build
    def connect(s):
        s.out @= ~(s.a ^ s.b)


# Declaring wires
# Logic, &, |, ~
class WireDecl(RawModule):
    """https://hdlbits.01xz.net/wiki/Wire_decl"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.c = Input()
        s.d = Input()
        s.out = Output()
        s.out_n = Output()

    @build
    def declare(s):
        s.w1 = Logic()
        s.w2 = Logic()

    @build
    def connect(s):
        s.w1 @= s.a & s.b
        s.w2 @= s.c & s.d
        s.out @= s.w1 | s.w2
        s.out_n @= ~s.out


# Vectors
#

# Vectors
# Input(3), []
class Vector0(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector0"""

    @build
    def ports(s):
        s.vec = Input(3)
        s.outv = Output(3)
        s.o0 = Output()
        s.o1 = Output()
        s.o2 = Output()

    @build
    def connect(s):
        s.outv @= s.vec
        s.o0 @= s.vec[0]
        s.o1 @= s.vec[1]
        s.o2 @= s.vec[2]


# Vectors in more detail
# @= ...[]
class Vector1(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector1"""

    @build
    def ports(s):
        s.in_ = Input(16)
        s.out_hi = Output(8)
        s.out_lo = Output(8)

    @build
    def connect(s):
        s.out_hi @= s.in_[8:]
        s.out_lo @= s.in_[:8]


# Vector part select
# ...[] @= ...[]
class Vector2(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector2"""

    @build
    def ports(s):
        s.in_ = Input(32)
        s.out = Output(32)

    @build
    def connect(s):
        s.out[24:] @= s.in_[:8]
        s.out[16:24] @= s.in_[8:16]
        s.out[8:16] @= s.in_[16:24]
        s.out[:8] @= s.in_[24:]


# Bitwise operators
# or, ...[] @=
class Vectorgates(RawModule):
    """https://hdlbits.01xz.net/wiki/Vectorgates"""

    @build
    def ports(s):
        s.a = Input(3)
        s.b = Input(3)
        s.out_or_bitwise = Output(3)
        s.out_or_logical = Output()
        s.out_not = Output(6)

    @build
    def connect(s):
        s.out_or_bitwise @= s.a | s.b
        s.out_or_logical @= Bool(s.a or s.b)
        s.out_not[:3] @= ~s.a
        s.out_not[3:] @= ~s.b


# Four-input gates
# reduce and/or/xor
class Gates4(RawModule):
    """https://hdlbits.01xz.net/wiki/Gates4"""

    @build
    def port(s):
        s.in_ = Input(4)
        s.out_and = Output()
        s.out_or = Output()
        s.out_xor = Output()

    @build
    def connect(s):
        s.out_and @= s.in_.AO
        s.out_or @= s.in_.NZ
        s.out_xor @= s.in_.P


# Vector concatenation operator
# cat(), b2()
class Vector3(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector3"""

    @build
    def ports(s):
        s.a = Input(5)
        s.b = Input(5)
        s.c = Input(5)
        s.d = Input(5)
        s.e = Input(5)
        s.f = Input(5)
        s.w = Output(8)
        s.x = Output(8)
        s.y = Output(8)
        s.z = Output(8)

    @build
    def connect(s):
        cat(s.w, s.x, s.y, s.z)[:] @= cat(
            s.a, s.b, s.c, s.d, s.e, s.f, b2(0b11)
        )


# Vector reversal 1
# /= cat()
class Vectorrev1(RawModule):
    """https://hdlbits.01xz.net/wiki/Vectorr"""

    @build
    def ports(s):
        s.in_ = Input(8)
        s.out = Output(8)

    @build
    def connect(s):
        s.out @= cat(
            s.in_[0],
            s.in_[1],
            s.in_[2],
            s.in_[3],
            s.in_[4],
            s.in_[5],
            s.in_[6],
            s.in_[7],
        )


# cat()[:] @= ...
class Vectorrev1_cat_lhs(RawModule):
    """https://hdlbits.01xz.net/wiki/Vectorr"""

    @build
    def ports(s):
        s.in_ = Input(8)
        s.out = Output(8)

    @build
    def connect(s):
        cat(
            s.out[0],
            s.out[1],
            s.out[2],
            s.out[3],
            s.out[4],
            s.out[5],
            s.out[6],
            s.out[7],
        )[:] @= s.in_


# Replication operator
# cat(rep(),...)
class Vector4(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector4"""

    @build
    def ports(s):
        s.in_ = Input(8)
        s.out = Output(32)

    @build
    def connect(s):
        s.out @= cat(rep(24, s.in_[7]), s.in_)


# More replication
# cat()**5
class Vector5(RawModule):
    """https://hdlbits.01xz.net/wiki/Vector5"""

    @build
    def ports(s):
        s.a = Input()
        s.b = Input()
        s.c = Input()
        s.d = Input()
        s.e = Input()
        s.out = Output(25)

    @build
    def declare(s):
        s.top = Logic(25)
        s.bottom = Logic(25)

    @build
    def connect(s):
        s.top @= cat(
            rep(5, s.a), rep(5, s.b), rep(5, s.c), rep(5, s.d), rep(5, s.e)
        )
        s.bottom @= cat(s.a, s.b, s.c, s.d, s.e) ** 5
        s.out @= ~s.top ^ s.bottom
