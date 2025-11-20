# Tests for HDLBits examples, modules hierarchy
#

import comopy.testcases.ex_HDLBits_modules as ex
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestModuleInst(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        out = Output()

    TV = [
        IO(),
        (0b1, 0b1, 0b1),
        (0b1, 0b0, 0b0),
        (0b0, 0b1, 0b0),
        (0b0, 0b0, 0b0),
    ]

    def test_module_inst(self):
        self.simulate(ex.ModuleInst(), self.TV)
        # self.simulate(ex.ModuleInst_local(), self.TV)


class TestModuleArgs(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        d = Input()
        out1 = Output()
        out2 = Output()

    TV = [
        IO(),
        (0b1, 0b1, 0b0, 0b0, 0b1, 0b0),
        (0b1, 0b0, 0b1, 0b0, 0b0, 0b1),
        (0b0, 0b1, 0b0, 0b1, 0b0, 0b1),
        (0b1, 0b1, 0b1, 0b1, 0b1, 0b1),
        (0b0, 0b0, 0b0, 0b0, 0b0, 0b0),
    ]

    def test_module_args(self):
        self.simulate(ex.Module_pos(), self.TV)
        self.simulate(ex.Module_name(), self.TV)


class TestModuleShift(BaseTestCase):
    class IO(IOStruct):
        clk = Input()
        d = Input()
        q = Output()

    TV = [
        IO(),
        (0b0, 0b1, 0b1),
        (0b1, 0b0, 0b0),
        (0b0, 0b0, 0b0),
        (0b1, 0b1, 0b1),
    ]

    def test_module_shift(self):
        self.simulate(ex.Module_shift(), self.TV)
        self.simulate(ex.Module_shift_autowire(), self.TV)


class TestModuleShift8(BaseTestCase):
    class IO(IOStruct):
        d = Input(8)
        sel = Input(2)
        q = Output(8)

    TV = [
        IO(),
        (0b10101010, 0b00, 0b10101010),
        (0b11110000, 0b01, 0b11110000),
        (0b00001111, 0b10, 0b11110000),
        (0b11111111, 0b11, 0b11110000),
        (0b01010101, 0b01, 0b01010101),
    ]

    def test_module_shift8(self):
        self.simulate(ex.Module_shift8(), self.TV)
