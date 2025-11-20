# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
HDLBits examples: sequential logic.

See: https://hdlbits.01xz.net
"""

from comopy import *
from comopy import Module, RawModule, build, seq  # for type checking


# D flip-flop
# @seq
class Dff_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff"""

    @build
    def ports(s):
        s.clk = Input()
        s.d = Input()
        s.q = Output()

    @seq
    def update_ff(s, posedge="clk"):
        s.q <<= s.d


class Dff(Module):
    """https://hdlbits.01xz.net/wiki/Dff"""

    @build
    def ports(s):
        s.d = Input()
        s.q = Output()

    @seq
    def update_ff(s):
        s.q <<= s.d


# D flip-flops
# @seq, vector
class Dff8_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff8"""

    @build
    def ports(s):
        s.clk = Input()
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s, posedge="clk"):
        s.q <<= s.d


class Dff8(Module):
    """https://hdlbits.01xz.net/wiki/Dff8"""

    @build
    def ports(s):
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s):
        s.q <<= s.d


# DFF with reset
class Dff8r_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff8r"""

    @build
    def ports(s):
        s.clk = Input()
        s.reset = Input()
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s, posedge="clk"):
        if s.reset:
            s.q <<= 0
        else:
            s.q <<= s.d


class Dff8r(Module):
    """https://hdlbits.01xz.net/wiki/Dff8r"""

    @build
    def ports(s):
        s.reset = Input()
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s):
        if s.reset:
            s.q <<= 0
        else:
            s.q <<= s.d


# DFF with reset value
# negedge
class Dff8p_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff8p"""

    @build
    def ports(s):
        s.clk = Input()
        s.reset = Input()
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s, negedge="clk"):
        if s.reset:
            s.q <<= b8(0x34)
        else:
            s.q <<= s.d


# DFF with asynchronous reset
# posedge
class Dff8ar_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff8ar"""

    @build
    def ports(s):
        s.clk = Input()
        s.areset = Input()  # active high asynchronous reset
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s, posedge=("clk", "areset")):
        if s.areset:
            s.q <<= 0
        else:
            s.q <<= s.d


class Dff8ar(Module):
    """https://hdlbits.01xz.net/wiki/Dff8ar"""

    @build
    def ports(s):
        s.areset = Input()  # active high asynchronous reset
        s.d = Input(8)
        s.q = Output(8)

    @seq
    def update_ff(s, posedge="areset"):
        if s.areset:
            s.q <<= 0
        else:
            s.q <<= s.d


# DFF with byte enable
class Dff16e_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Dff16e"""

    @build
    def ports(s):
        s.clk = Input()
        s.resetn = Input()  # synchronous, active-low reset
        s.byteena = Input(2)  # byte enable: [1] for d[15:8], [0] for d[7:0]
        s.d = Input(16)
        s.q = Output(16)

    @seq
    def update_ff(s, posedge="clk"):
        if ~s.resetn:
            s.q <<= 0
        else:
            if s.byteena[0]:
                s.q[:8] <<= s.d[:8]
            if s.byteena[1]:
                s.q[8:] <<= s.d[8:]


class Dff16e(Module):
    """https://hdlbits.01xz.net/wiki/Dff16e"""

    @build
    def ports(s):
        s.resetn = Input()  # synchronous, active-low reset
        s.byteena = Input(2)  # byte enable: [1] for d[15:8], [0] for d[7:0]
        s.d = Input(16)
        s.q = Output(16)

    @seq
    def update_ff(s):
        if ~s.resetn:
            s.q <<= 0
        else:
            if s.byteena[0]:
                s.q[:8] <<= s.d[:8]
            if s.byteena[1]:
                s.q[8:] <<= s.d[8:]


# Mux and DFF
class MuxDff_raw(RawModule):
    """https://hdlbits.01xz.net/wiki/Mt2015_muxdff"""

    @build
    def ports(s):
        s.clk = Input()
        s.L = Input()
        s.r_in = Input()
        s.q_in = Input()
        s.Q = Output()

    @seq
    def update_q(s, posedge="clk"):
        s.Q <<= s.r_in if s.L else s.q_in


class MuxDff(Module):
    """https://hdlbits.01xz.net/wiki/Mt2015_muxdff"""

    @build
    def ports(s):
        s.L = Input()
        s.r_in = Input()
        s.q_in = Input()
        s.Q = Output()

    @seq
    def update_q(s):
        s.Q <<= s.r_in if s.L else s.q_in


# Detect an edge


# Detect both edges


# Edge capture register


# Dual-edge triggered flip-flop
