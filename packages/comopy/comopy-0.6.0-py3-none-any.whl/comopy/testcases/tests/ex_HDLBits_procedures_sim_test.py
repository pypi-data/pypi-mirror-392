# Tests for HDLBits examples, procedures
#

import comopy.testcases.ex_HDLBits_procedures as ex
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestAlwaysblock1(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        out_assign = Output()
        out_alwaysblock = Output()

    TV = [
        IO(),
        (0b0, 0b0, 0b0, 0b0),
        (0b0, 0b1, 0b0, 0b0),
        (0b1, 0b1, 0b1, 0b1),
    ]

    def test(self):
        self.simulate(ex.Alwaysblock1(), self.TV)


class TestAlwaysblock2(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        a = Input()
        b = Input()
        out_assign = Output()
        out_always_comb = Output()
        out_always_ff = Output()

    TV_posedge = [
        IO(),
        (0, 0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0, 0),  # cycle1
        (0, 0, 1, 1, 1, 0),
        (1, 0, 1, 1, 1, 1),  # cycle2
        (0, 0, 0, 0, 0, 1),
        (1, 0, 0, 0, 0, 0),  # cycle3
        (0, 1, 0, 1, 1, 0),
        (1, 1, 0, 1, 1, 1),  # cycle4
        (0, 1, 1, 0, 0, 1),
        (1, 1, 1, 0, 0, 0),  # cycle5
    ]

    def test_posedge(self):
        self.simulate(ex.Alwaysblock2(), self.TV_posedge)

    TV_autoclk = [
        IO(),
        (None, 0, 0, 0, 0, 0),
        (None, 0, 1, 1, 1, 1),
        (None, 1, 1, 0, 0, 0),
        (None, 1, 0, 1, 1, 1),
    ]

    def test_autoclk(self):
        self.simulate(ex.Alwaysblock2_autoclk(), self.TV_autoclk)


class TestAlwaysIf(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        sel_b1 = Input()
        sel_b2 = Input()
        out_assign = Output()
        out_always = Output()

    TV = [
        IO(),
        (0, 1, 0, 0, 0, 0),
        (0, 1, 0, 1, 0, 0),
        (0, 1, 1, 0, 0, 0),
        (0, 1, 1, 1, 1, 1),
    ]

    def test(self):
        self.simulate(ex.Always_if(), self.TV)


class TestAlwaysIf2(BaseTestCase):
    class IO(IOStruct):
        cpu_overheated = Input()
        shut_off_computer = Output()
        arrived = Input()
        gas_tank_empty = Input()
        keep_driving = Output()

    TV = [
        IO(),
        (0, 0, 0, 0, 1),
        (1, 1, 0, 0, 1),
        (1, 1, 1, 0, 0),
        (1, 1, 0, 0, 1),
        (1, 1, 0, 1, 0),
    ]

    def test(self):
        self.simulate(ex.Always_if2(), self.TV)


class TestAlwaysCase(BaseTestCase):
    class IO(IOStruct):
        sel = Input(3)
        data0 = Input(4)
        data1 = Input(4)
        data2 = Input(4)
        data3 = Input(4)
        data4 = Input(4)
        data5 = Input(4)
        out = Output(4)

    TV = [
        IO(),
        (0, 1, 2, 3, 4, 5, 6, 1),
        (1, 1, 2, 3, 4, 5, 6, 2),
        (2, 1, 2, 3, 4, 5, 6, 3),
        (3, 1, 2, 3, 4, 5, 6, 4),
        (4, 1, 2, 3, 4, 5, 6, 5),
        (5, 1, 2, 3, 4, 5, 6, 6),
        (6, 1, 2, 3, 4, 5, 6, 0),
        (7, 1, 2, 3, 4, 5, 6, 0),
    ]

    def test(self):
        self.simulate(ex.Always_case(), self.TV)


class TestAlwaysCase2(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(4)
        pos = Output(2)

    TV = [
        IO(),
        (0b0000, 0),
        (0b0001, 0),
        (0b0010, 1),
        (0b0011, 0),
        (0b0100, 2),
        (0b0101, 0),
        (0b0110, 1),
        (0b0111, 0),
        (0b1000, 3),
        (0b1001, 0),
        (0b1010, 1),
        (0b1011, 0),
        (0b1100, 2),
        (0b1101, 0),
        (0b1110, 1),
        (0b1111, 0),
    ]

    def test(self):
        self.simulate(ex.Always_case2(), self.TV)


class TestAlwaysCasez(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(8)
        pos = Output(3)

    TV = [
        IO(),
        (0b00000000, 0),
        (0b00100001, 0),
        (0b00001010, 1),
        (0b00100100, 2),
        (0b01001000, 3),
        (0b01010000, 4),
        (0b10100000, 5),
        (0b01000000, 6),
        (0b10000000, 7),
    ]

    def test(self):
        self.simulate(ex.Always_casez(), self.TV)


class TestAlwaysNolatches(BaseTestCase):
    class IO(IOStruct):
        scancode = Input(16)
        left = Output()
        down = Output()
        right = Output()
        up = Output()

    TV = [
        IO(),
        (0xE06B, 1, 0, 0, 0),
        (0xE072, 0, 1, 0, 0),
        (0xE074, 0, 0, 1, 0),
        (0xE075, 0, 0, 0, 1),
        (0xE0FF, 0, 0, 0, 0),
    ]

    def test(self):
        self.simulate(ex.Always_nolatches(), self.TV)
