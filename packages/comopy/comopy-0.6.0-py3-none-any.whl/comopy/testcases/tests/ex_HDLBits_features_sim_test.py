# Tests for HDLBits examples, more Verilog features
#

import comopy.testcases.ex_HDLBits_features as ex
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestConditional(BaseTestCase):
    class IO(IOStruct):
        a = Input(8)
        b = Input(8)
        c = Input(8)
        d = Input(8)
        min = Output(8)

    TV = [
        IO(),
        (0x12, 0x34, 0x56, 0x78, 0x12),
        (0x34, 0x12, 0x56, 0x78, 0x12),
        (0x56, 0x34, 0x12, 0x78, 0x12),
        (0x78, 0x34, 0x56, 0x12, 0x12),
    ]

    def test(self):
        self.simulate(ex.Conditional(), self.TV)


class TestReduction(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(8)
        parity = Output()

    TV = [IO(), (0x00, 0), (0x01, 1), (0x0F, 0), (0xFF, 0), (0xAB, 1)]

    def test(self):
        self.simulate(ex.Reduction(), self.TV)


class TestGates100(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(100)
        out_and = Output()
        out_or = Output()
        out_xor = Output()

    TV = [
        IO(),
        (0x0, 0, 0, 0),
        (0xABCDEFFE, 0, 1, 0),
        (0xFFFFFFFF, 0, 1, 0),
        (0x111111111, 0, 1, 1),
    ]

    def test(self):
        self.simulate(ex.Gates100(), self.TV)


class TestVector100r(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(100)
        out = Output(100)

    TV = [
        IO(),
        (0, 0),
        (-1, -1),
        (0x55555555_55555555_55555555_5, 0xAAAAAAAA_AAAAAAAA_AAAAAAAA_A),
    ]

    def test(self):
        self.simulate(ex.Vector100r(), self.TV)


class TestPopcount255(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(255)
        out = Output(8)

    TV = [
        IO(),
        (0, 0),
        (1, 1),
        (0b1111_1111, 8),
        (0b1010_1010, 4),
    ]

    def test(self):
        self.simulate(ex.Popcount255(), self.TV)
