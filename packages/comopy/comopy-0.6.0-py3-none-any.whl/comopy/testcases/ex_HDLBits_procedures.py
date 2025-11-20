# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDLBits examples: procedures.

See: https://hdlbits.01xz.net
"""

from comopy import *
from comopy import Module, RawModule, build, comb, seq  # for type checking


# Always blocks (combinational)
# @comb, @=
class Alwaysblock1(RawModule):
    """https://hdlbits.01xz.net/wiki/Alwayblock1"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.out_assign = Output()
        s.out_alwaysblock = Output()
        s.out_assign @= s.a & s.b

    @comb
    def update(s):
        s.out_alwaysblock /= s.a & s.b


# Always blocks (clocked)
# @seq
class Alwaysblock2(RawModule):
    """https://hdlbits.01xz.net/wiki/Alwayblock2"""

    @build
    def build_all(s):
        s.clk = Input()
        s.a = Input()
        s.b = Input()
        s.out_assign = Output()
        s.out_always_comb = Output()
        s.out_always_ff = Output()
        s.out_assign @= s.a ^ s.b

    @comb
    def update(s):
        s.out_always_comb /= s.a ^ s.b

    @seq
    def update_ff(s, posedge="clk"):
        s.out_always_ff <<= s.a ^ s.b


# HDL.Module
class Alwaysblock2_autoclk(Module):
    """https://hdlbits.01xz.net/wiki/Alwayblock2"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.out_assign = Output()
        s.out_always_comb = Output()
        s.out_always_ff = Output()
        s.out_assign @= s.a ^ s.b

    @comb
    def update(s):
        s.out_always_comb /= s.a ^ s.b

    @seq
    def update_ff(s):
        s.out_always_ff <<= s.a ^ s.b


# If statement
# if, else
class Always_if(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_if"""

    @build
    def build_all(s):
        s.a = Input()
        s.b = Input()
        s.sel_b1 = Input()
        s.sel_b2 = Input()
        s.out_assign = Output()
        s.out_always = Output()

    @build
    def assign(s):
        s.out_assign @= s.b if s.sel_b1 & s.sel_b2 else s.a

    @comb
    def update(s):
        if s.sel_b1 & s.sel_b2:
            s.out_always /= s.b
        else:
            s.out_always /= s.a


# If statement latches
# Avoiding latch
class Always_if2(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_if2"""

    @build
    def build_all(s):
        s.cpu_overheated = Input()
        s.shut_off_computer = Output()
        s.arrived = Input()
        s.gas_tank_empty = Input()
        s.keep_driving = Output()

    @comb
    def computer(s):
        if s.cpu_overheated:
            s.shut_off_computer /= 1
        else:
            s.shut_off_computer /= 0

    @comb
    def car(s):
        if ~s.arrived:
            s.keep_driving /= ~s.gas_tank_empty
        else:
            s.keep_driving /= 0


# Case statement
# case, int patterns
class Always_case(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_case"""

    @build
    def build_all(s):
        s.sel = Input(3)
        s.data0 = Input(4)
        s.data1 = Input(4)
        s.data2 = Input(4)
        s.data3 = Input(4)
        s.data4 = Input(4)
        s.data5 = Input(4)
        s.out = Output(4)

    @comb
    def update(s):
        match s.sel:
            case 0:
                s.out /= s.data0
            case 1:
                s.out /= s.data1
            case 2:
                s.out /= s.data2
            case 3:
                s.out /= s.data3
            case 4:
                s.out /= s.data4
            case 5:
                s.out /= s.data5
            case _:
                s.out /= 0


# Priority encoder
# case, Bits patterns
class Always_case2(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_case2"""

    @build
    def build_all(s):
        s.in_ = Input(4)
        s.pos = Output(2)

    @comb
    def update(s):
        match s.in_:
            case 0b0000:
                s.pos /= 0
            case 0b0001:
                s.pos /= 0
            case 0b0010:
                s.pos /= 1
            case 0b0011:
                s.pos /= 0
            case 0b0100:
                s.pos /= 2
            case 0b0101:
                s.pos /= 0
            case 0b0110:
                s.pos /= 1
            case 0b0111:
                s.pos /= 0
            case 0b1000:
                s.pos /= 3
            case 0b1001:
                s.pos /= 0
            case 0b1010:
                s.pos /= 1
            case 0b1011:
                s.pos /= 0
            case 0b1100:
                s.pos /= 2
            case 0b1101:
                s.pos /= 0
            case 0b1110:
                s.pos /= 1
            case 0b1111:
                s.pos /= 0


# Priority encoder with casez
class Always_casez(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_casez"""

    @build
    def build_all(s):
        s.in_ = Input(8)
        s.pos = Output(3)

    @comb
    def update(s):
        match s.in_:
            case "????_???1":
                s.pos /= 0
            case "????_??10":
                s.pos /= 1
            case "????_?100":
                s.pos /= 2
            case "????_1000":
                s.pos /= 3
            case "???1_0000":
                s.pos /= 4
            case "??10_0000":
                s.pos /= 5
            case "?100_0000":
                s.pos /= 6
            case "1000_0000":
                s.pos /= 7
            case _:
                s.pos /= 0


# Avoiding latches
class Always_nolatches(RawModule):
    """https://hdlbits.01xz.net/wiki/Always_nolatches"""

    @build
    def build_all(s):
        s.scancode = Input(16)
        s.left = Output()
        s.down = Output()
        s.right = Output()
        s.up = Output()

    @comb
    def update(s):
        s.left /= 0
        s.down /= 0
        s.right /= 0
        s.up /= 0
        match s.scancode:
            case 0xE06B:
                s.left /= 1
            case 0xE072:
                s.down /= 1
            case 0xE074:
                s.right /= 1
            case 0xE075:
                s.up /= 1
            case _:
                pass  # pre-assigned before case
