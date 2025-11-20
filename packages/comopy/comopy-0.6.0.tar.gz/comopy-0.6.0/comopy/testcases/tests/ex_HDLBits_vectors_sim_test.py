# Tests for HDLBits examples, vectors
#

import comopy.testcases.ex_HDLBits_conn as ex_conn
import comopy.testcases.ex_HDLBits_no_conn as ex_comb
from comopy.hdl import Input, IOStruct, Output
from comopy.testcases.base_test_case import BaseTestCase


class TestVector0(BaseTestCase):
    class IO(IOStruct):
        vec = Input(3)
        outv = Output(3)
        o0 = Output()
        o1 = Output()
        o2 = Output()

    TV = [
        IO(),
        (0b000, 0b000, 0b0, 0b0, 0b0),
        (0b001, 0b001, 0b1, 0b0, 0b0),
        (0b011, 0b011, 0b1, 0b1, 0b0),
        (0b111, 0b111, 0b1, 0b1, 0b1),
    ]

    def test_vector0(self):
        self.simulate(ex_comb.Vector0(), self.TV)
        self.simulate(ex_conn.Vector0(), self.TV)


class TestVector1(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(16)
        out_hi = Output(8)
        out_lo = Output(8)

    TV = [
        IO(),
        (0x0000, 0x00, 0x00),
        (0xFF77, 0xFF, 0x77),
        (0xABCD, 0xAB, 0xCD),
    ]

    def test_vector1(self):
        self.simulate(ex_comb.Vector1(), self.TV)
        self.simulate(ex_conn.Vector1(), self.TV)


class TestVector2(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(32)
        out = Output(32)

    TV = [IO(), (0x12345678, 0x78563412), (0x11223344, 0x44332211)]

    def test_vector2(self):
        self.simulate(ex_comb.Vector2(), self.TV)
        self.simulate(ex_conn.Vector2(), self.TV)


class TestVectorgates(BaseTestCase):
    class IO(IOStruct):
        a = Input(3)
        b = Input(3)
        out_or_bitwise = Output(3)
        out_or_logical = Output()
        out_not = Output(6)

    TV = [
        IO(),
        (0b000, 0b000, 0b000, 0b0, 0b111111),
        (0b001, 0b000, 0b001, 0b1, 0b111110),
        (0b101, 0b100, 0b101, 0b1, 0b011010),
    ]

    def test_vectorgates(self):
        self.simulate(ex_comb.Vectorgates(), self.TV)
        self.simulate(ex_conn.Vectorgates(), self.TV)


class TestGates4(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(4)
        out_and = Output()
        out_or = Output()
        out_xor = Output()

    TV = [
        IO(),
        (0b0000, 0b0, 0b0, 0b0),
        (0b1000, 0b0, 0b1, 0b1),
        (0b1100, 0b0, 0b1, 0b0),
        (0b1110, 0b0, 0b1, 0b1),
        (0b1111, 0b1, 0b1, 0b0),
    ]

    def test_gates4(self):
        self.simulate(ex_comb.Gates4(), self.TV)
        self.simulate(ex_conn.Gates4(), self.TV)


class TestVector3(BaseTestCase):
    class IO(IOStruct):
        a = Input(5)
        b = Input(5)
        c = Input(5)
        d = Input(5)
        e = Input(5)
        f = Input(5)
        w = Output(8)
        x = Output(8)
        y = Output(8)
        z = Output(8)

    TV = [
        IO(),
        (
            0b00001,
            0b00010,
            0b00100,
            0b01000,
            0b10000,
            0b11111,
            0b00001000,
            0b10001000,
            0b10001000,
            0b01111111,
        ),
        (
            0b11111,
            0b00000,
            0b11111,
            0b00000,
            0b11111,
            0b00000,
            0b11111000,
            0b00111110,
            0b00001111,
            0b10000011,
        ),
    ]

    def test_vector3(self):
        self.simulate(ex_comb.Vector3(), self.TV)
        self.simulate(ex_conn.Vector3(), self.TV)


class TestVectorrev1(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(8)
        out = Output(8)

    TV = [
        IO(),
        (0b11000110, 0b01100011),
        (0b11110000, 0b00001111),
        (0b10110111, 0b11101101),
    ]

    def test_vectorrev1(self):
        self.simulate(ex_comb.Vectorrev1(), self.TV)
        self.simulate(ex_conn.Vectorrev1(), self.TV)


class TestVector4(BaseTestCase):
    class IO(IOStruct):
        in_ = Input(8)
        out = Output(32)

    TV = [IO(), (0x81, 0xFFFFFF81), (0x7F, 0x0000007F)]

    def test_vector4(self):
        self.simulate(ex_comb.Vector4(), self.TV)
        self.simulate(ex_conn.Vector4(), self.TV)


class TestVector5(BaseTestCase):
    class IO(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        d = Input()
        e = Input()
        out = Output(25)

    TV = [
        IO(),
        (0b1, 0b1, 0b1, 0b0, 0b0, 0b0001110011100111000001100011),
        (0b0, 0b0, 0b1, 0b1, 0b1, 0b0001100011000001110011100111),
    ]

    def test_vector5(self):
        self.simulate(ex_comb.Vector5(), self.TV)
        self.simulate(ex_conn.Vector5(), self.TV)
