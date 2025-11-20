# Tests for BaseTestCase
#

import pytest

import comopy.hdl as HDL
from comopy.bits import b4  # type: ignore
from comopy.testcases.base_test_case import BaseTestCase


class TestRawModule(BaseTestCase):
    # Module
    class Top(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)
            s.in3 = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):
            s.out /= s.in1 | s.in2 ^ s.in3

    # I/O
    class IO(HDL.IOStruct):
        in1 = HDL.Input(4)
        in2 = HDL.Input(4)
        in3 = HDL.Input(4)
        out = HDL.Output(4)

    # Test vector
    TV = [
        IO(),
        (0x0, 0x5, 0x5, b4(0x0)),
        (0x1, 0x1, 0x2, b4(0x3)),
    ]

    # Expected SystemVerilog output
    SV = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in1 | in2 ^ in3;\n"
        "\n"
    )

    def test_raw_module(self):
        self.simulate(self.Top(name="top"), self.TV)
        self.translate(self.Top(name="top"), self.SV)


class Top(HDL.RawModule):
    @HDL.build
    def build_all(s):
        s.in1 = HDL.Input(4)
        s.in2 = HDL.Input(4)
        s.in3 = HDL.Input(4)
        s.out = HDL.Output(4)

    @HDL.comb
    def update(s):
        s.out /= s.in1 | s.in2 ^ s.in3


class TestNoTV(BaseTestCase):
    top = Top(name="top")

    def test_no_tv(self):
        with pytest.raises(RuntimeError, match=r"No TV for DUT module Top"):
            self.simulate(self.top, [])


class TestNoIO(BaseTestCase):
    top = Top(name="top")

    TV_Top = [
        (0x0, 0x55, 0x0),
        (0x1, 0x12, 0x3),
    ]

    def test_no_io(self):
        with pytest.raises(RuntimeError, match=r"No IOStruct at TV\[0\]"):
            self.simulate(self.top, self.TV_Top)


class TestMismatchedData(BaseTestCase):
    top = Top(name="top")

    class IO(HDL.IOStruct):
        in1 = HDL.Input(4)
        in2 = HDL.Input(4)
        in3 = HDL.Input(4)
        out = HDL.Output(4)

    TV = [
        IO(),
        (0x0, 0x5, 0x5, 0x0),
        (0x1, 0x1, 0x2),
    ]

    def test_mismatched_data(self):
        with pytest.raises(RuntimeError, match=r"TV\[2\] doesn't match"):
            self.simulate(self.top, self.TV)


class TestMismatchedIO(BaseTestCase):
    top = Top(name="top")

    class IO(HDL.IOStruct):
        in_ = HDL.Input(4)
        out = HDL.Output(4)

    TV = [
        IO(),
        (0x0, 0x5),
        (0x1, 0x1),
    ]

    def test_mismatched_io(self):
        with pytest.raises(RuntimeError, match=r"IO\(\) .* doesn't match"):
            self.simulate(self.top, self.TV)


class TestCombFailed(BaseTestCase):
    top = Top(name="top")

    class IO(HDL.IOStruct):
        in1 = HDL.Input(4)
        in2 = HDL.Input(4)
        in3 = HDL.Input(4)
        out = HDL.Output(4)

    TV = [
        IO(),
        (0x0, 0x5, 0x5, 0x0),
        (0x1, 0x1, 0x2, 0x3),
        (0x2, 0x1, 0x1, 0x5),
    ]

    def test_comb_failed(self):
        with pytest.raises(RuntimeError, match=r"out\(0x2\) != 0x5 : TV\[3\]"):
            self.simulate(self.top, self.TV)
