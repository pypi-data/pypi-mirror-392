# ComoPy: Co-modeling tools for hardware generation with Python
#
# Copyright (C) 2024-2025 Microprocessor R&D Center (MPRC), Peking University
# SPDX-License-Identifier: MIT
#
# Author: Chun Yang

"""
Examples demonstrating class inheritance in ComoPy HDL modules.
"""

from comopy import Input, Logic, Output, RawModule, build, comb


class CalcInterface(RawModule):
    @build
    def ports(s):
        s.in1 = Input(8)
        s.in2 = Input(8)
        s.out = Output(8)
        s.a = Logic(8)
        s.b = Logic(8)
        s.res = Logic(8)

    @build
    def input(s):
        s.a @= s.in1
        s.b @= s.in2

    @build
    def output(s):
        s.out @= s.res


# Single inheritance
class NorImpl(CalcInterface):
    @build
    def result_nor(s):
        s.nor = Logic(8)

    @comb
    def calc_nor(s):
        s.nor /= ~(s.a | s.b)


# Single inheritance
class XnorImpl(CalcInterface):
    @build
    def result_xnor(s):
        s.xnor = Logic(8)

    @comb
    def calc_xnor(s):
        s.xnor /= ~(s.a ^ s.b)


# Multiple inheritance
class CalcUnit(NorImpl, XnorImpl):
    @build
    def result(s):
        s.res @= s.nor & s.xnor


class CalcDebug(CalcUnit):
    @build
    def debug_result(s):
        s.debug = Output(8)
        s.debug @= s.res


class Inject(CalcDebug):
    # Override
    @build
    def input(s):
        s.a @= s.in1 & s.in2
        s.b @= s.in1 | s.in2


class Inject2(CalcDebug):
    # Override and call super
    @build
    def input(s):
        super().input()
        s.inject_a = Input(8)
        s.inject_b = Input(8)
        s.inject_a @= s.a
        s.inject_b @= s.b
