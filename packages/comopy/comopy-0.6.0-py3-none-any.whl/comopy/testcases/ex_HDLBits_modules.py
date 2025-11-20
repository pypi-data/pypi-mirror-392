# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDLBits examples: modules hierarchy.

See: https://hdlbits.01xz.net
"""

from comopy import *
from comopy import Module, RawModule, build, comb, seq  # for type checking


# Module
# Raw module instantiation
class mod_a1(RawModule):
    @build
    def build_all(s):
        s.in1 = Input()
        s.in2 = Input()
        s.out = Output()
        s.out @= s.in1 & s.in2


class ModuleInst(RawModule):
    """https://hdlbits.01xz.net/wiki/Module"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.out = Output()
        s.inst = mod_a1()
        s.inst.in1 @= s.a
        s.inst.in2 @= s.b
        s.out @= s.inst.out


class ModuleInst_local(RawModule):
    """https://hdlbits.01xz.net/wiki/Module"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.out = Output()
        s.inst = m = mod_a1()
        m.in1 @= s.a
        m.in2 @= s.b
        s.out @= s.inst.out


# Connecting ports by position
class mod_a2(RawModule):
    @build
    def build_all(s):
        s.out1 = Output()
        s.out2 = Output()
        s.in1 = Input()
        s.in2 = Input()
        s.in3 = Input()
        s.in4 = Input()
        s.out1 @= s.in1 & s.in2
        s.out2 @= s.in3 | s.in4


class Module_pos(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_pos"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.c = Input()
        s.d = Input()
        s.out1 = Output()
        s.out2 = Output()
        s.inst = mod_a2(s.out1, s.out2, s.a, s.b, s.c, s.d)


# Connecting ports by name
class Module_name(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_name"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.c = Input()
        s.d = Input()
        s.out1 = Output()
        s.out2 = Output()
        s.inst = mod_a2(
            in1=s.a, in2=s.b, in3=s.c, in4=s.d, out1=s.out1, out2=s.out2
        )


# Three modules
# Multiple instances, one submodule declaration
class my_dff(RawModule):  # passthrough only for testing
    @build
    def build_all(s):
        s.clk = Input()
        s.d = Input()
        s.q = Output()
        s.q @= s.d


class Module_shift(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_shift"""

    @build
    def build_all(s):
        s.clk = Input()
        s.d = Input()
        s.q = Output()
        s.a = Logic()
        s.b = Logic()
        s.dff0 = my_dff(s.clk, s.d, s.a)
        s.dff1 = my_dff(s.clk, s.a, s.b)
        s.dff2 = my_dff(s.clk, s.b, s.q)


# Connect to ports of other instance, partial ports
class Module_shift_autowire(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_shift"""

    @build
    def build_all(s):
        s.clk = Input()
        s.d = Input()
        s.q = Output()
        s.dff0 = my_dff(clk=s.clk, d=s.d)
        s.dff1 = my_dff(s.clk, s.dff0.q)
        s.dff2 = my_dff(s.clk, s.dff1.q, s.q)


# Modules and vectors
# multiplexer
class my_dff8(Module):
    @build
    def build_all(s):
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s):
        s.q <<= s.d


class Module_shift8(Module):
    """https://hdlbits.01xz.net/wiki/Module_shift8"""

    @build
    def build_all(s):
        s.d = Input(8)
        s.sel = Input(2)
        s.q = Output(8)
        s.dff0 = my_dff8(s.d)
        s.dff1 = my_dff8(s.dff0.q)
        s.dff2 = my_dff8(s.dff1.q)

    @comb
    def update(s):
        match s.sel:
            case 0:
                s.q /= s.d
            case 1:
                s.q /= s.dff0.q
            case 2:
                s.q /= s.dff1.q
            case 3:
                s.q /= s.dff2.q


# Adder 1
class add16(RawModule):
    @build
    def build_all(s):
        s.a = Input(16)
        s.b = Input(16)
        s.cin = Input()
        s.sum = Output(16)
        s.cout = Output()
        cat(s.cout, s.sum)[:] @= s.a.ext(17) + s.b.ext(17) + s.cin.ext(17)


class Module_add(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_add"""

    @build
    def build_all(s):
        s.a = Input(32)
        s.b = Input(32)
        s.sum = Output(32)
        s.lo = add16(s.a[:16], s.b[:16], 0, s.sum[:16])
        s.hi = add16(s.a[16:], s.b[16:], s.lo.cout, s.sum[16:])


# Adder 2
# top_module is the same as Module_add
class Module_fadd1(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_fadd"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.cin = Input()
        s.sum = Output()
        s.cout = Output()
        s.sum @= s.a ^ s.b ^ s.cin
        s.cout @= s.a & s.b | s.a & s.cin | s.b & s.cin


# Carry-select adder
class Module_cseladd(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_cseladd"""

    @build
    def build_all(s):
        s.a = Input(32)
        s.b = Input(32)
        s.sum = Output(32)
        s.lo = add16(s.a[:16], s.b[:16], 0, s.sum[:16])
        s.hi0 = add16(s.a[16:], s.b[16:], 0)
        s.hi1 = add16(s.a[16:], s.b[16:], 1)
        s.sum[16:] @= s.hi1.sum if s.lo.cout else s.hi0.sum


# Adder-substractor
class Module_addsub(RawModule):
    """https://hdlbits.01xz.net/wiki/Module_addsub"""

    @build
    def build_all(s):
        s.a = Input(32)
        s.b = Input(32)
        s.sub = Input()
        s.sum = Output(32)
        s.b_sub = Logic(32)
        s.b_sub @= s.b ^ s.sub**32
        s.lo = add16(s.a[:16], s.b_sub[:16], s.sub, s.sum[:16])
        s.hi = add16(s.a[16:], s.b_sub[16:], s.lo.cout, s.sum[16:])
