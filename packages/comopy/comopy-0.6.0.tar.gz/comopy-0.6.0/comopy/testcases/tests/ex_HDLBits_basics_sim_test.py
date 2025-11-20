# Tests for HDLBits examples, basics
#

import comopy.testcases.ex_HDLBits_conn as ex_conn
import comopy.testcases.ex_HDLBits_no_conn as ex_comb
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestWire1(BaseTestCase):
    class IO(IOStruct):
        in_ = Input()
        out = Output()

    TV = [IO(), (0b1, 0b1), (0b0, 0b0)]

    def test_wire1(self):
        self.simulate(ex_comb.Wire1(), self.TV)
        self.simulate(ex_conn.Wire1(), self.TV)


class TestWire4(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        w = Output()
        x = Output()
        y = Output()
        z = Output()

    TV = [
        IO(),
        (0b1, 0b0, 0b1, 0b1, 0b0, 0b0, 0b1),
        (0b0, 0b1, 0b0, 0b0, 0b1, 0b1, 0b0),
    ]

    def test_wire4(self):
        self.simulate(ex_comb.Wire4(), self.TV)
        self.simulate(ex_conn.Wire4(), self.TV)


class TestNotgate(BaseTestCase):
    class IO(IOStruct):
        in_ = Input()
        out = Output()

    TV = [IO(), (0b1, 0b0), (0b0, 0b1)]

    def test_notgate(self):
        self.simulate(ex_comb.Notgate(), self.TV)
        self.simulate(ex_conn.Notgate(), self.TV)


class TestAndgate(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        out = Output()

    TV = [
        IO(),
        (0b0, 0b0, 0b0),
        (0b1, 0b0, 0b0),
        (0b0, 0b1, 0b0),
        (0b1, 0b1, 0b1),
    ]

    def test_andgate(self):
        self.simulate(ex_comb.Andgate(), self.TV)
        self.simulate(ex_conn.Andgate(), self.TV)


class TestNorgate(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        out = Output()

    TV = [
        IO(),
        (0b0, 0b0, 0b1),
        (0b1, 0b0, 0b0),
        (0b0, 0b1, 0b0),
        (0b1, 0b1, 0b0),
    ]

    def test_norgate(self):
        self.simulate(ex_comb.Norgate(), self.TV)
        self.simulate(ex_conn.Norgate(), self.TV)


class TestXnorgate(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        out = Output()

    TV = [
        IO(),
        (0b0, 0b0, 0b1),
        (0b1, 0b0, 0b0),
        (0b0, 0b1, 0b0),
        (0b1, 0b1, 0b1),
    ]

    def test_xnorgate(self):
        self.simulate(ex_comb.Xnorgate(), self.TV)
        self.simulate(ex_conn.Xnorgate(), self.TV)


class TestWireDecl(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        d = Input()
        out = Output()
        out_n = Output()

    TV = [
        IO(),
        (0b0, 0b0, 0b0, 0b0, 0b0, 0b1),
        (0b0, 0b0, 0b0, 0b1, 0b0, 0b1),
        (0b0, 0b1, 0b1, 0b1, 0b1, 0b0),
        (0b1, 0b1, 0b1, 0b1, 0b1, 0b0),
    ]

    def test_wiredecl(self):
        self.simulate(ex_comb.WireDecl(), self.TV)
        self.simulate(ex_conn.WireDecl(), self.TV)
