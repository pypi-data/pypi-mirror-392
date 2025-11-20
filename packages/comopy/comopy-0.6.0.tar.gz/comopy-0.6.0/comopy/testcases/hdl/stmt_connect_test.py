# Tests for HDL statement: connection (@=)
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    IOStruct,
    Logic,
    Output,
    RawModule,
    build,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestConnectValues(BaseTestCase):
    class ConnectValues(RawModule):
        @build
        def ports(s):
            s.in_scalar = Input()
            s.out_scalar = Output()
            s.in_vector = Input(4)
            s.out_vector = Output(4)
            s.out_bits = Output(8)
            s.out_int = Output(8)

        @build
        def declare(s):
            s.temp_scalar = Logic()
            s.temp_vector = Logic(4)

        @build
        def connect_scalar(s):
            s.temp_scalar @= s.in_scalar
            s.out_scalar @= s.temp_scalar

        @build
        def connect_vector(s):
            s.temp_vector @= s.in_vector
            s.out_vector @= s.temp_vector

        @build
        def connect_const(s):
            s.out_bits @= 1 + b8(2) & 3
            s.out_int @= 1 + 2 & 3

    class IO(IOStruct):
        in_scalar = Input()
        out_scalar = Output()
        in_vector = Input(4)
        out_vector = Output(4)
        out_bits = Output(8)
        out_int = Output(8)

    TV_connect = [
        IO(),
        (0, 0, 0b0000, 0b0000, 0x03, 0x03),
        (1, 1, 0b0101, 0b0101, 0x03, 0x03),
        (0, 0, 0b1010, 0b1010, 0x03, 0x03),
        (1, 1, 0b1111, 0b1111, 0x03, 0x03),
    ]
    SV_connect = (
        "  assign temp_scalar = in_scalar;\n"
        "  assign __out_scalar_bits = temp_scalar;\n"
        "  assign temp_vector = in_vector;\n"
        "  assign __out_vector_bits = temp_vector;\n"
        "  assign __out_bits_bits = 8'h1 + 8'h2 & 8'h3;\n"
        "  assign __out_int_bits = 8'h3;\n"
    )

    def test_connect(self):
        self.simulate(self.ConnectValues(), self.TV_connect)
        self.translate(self.ConnectValues(), self.SV_connect)


# Test driving parts of a signal
class TestConnectTargets(BaseTestCase):
    class ConnectTarget(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.out = Output(4)

    class IO(IOStruct):
        in_ = Input(8)
        out = Output(4)

    class ConnectSignal(ConnectTarget):
        @build
        def connect(s):
            s.out @= s.in_[:4]

    TV_signal = [IO(), (0xAB, 0xB), (0x12, 0x2)]
    SV_signal = "  assign __out_bits = in_[3:0];"

    def test_signal(self):
        self.simulate(self.ConnectSignal(), self.TV_signal)
        self.translate(self.ConnectSignal(), self.SV_signal)

    class ConnectIndex(ConnectTarget):
        @build
        def connect(s):
            s.out[0] @= s.in_[0]
            s.out[1] @= s.in_[2]
            s.out[2] @= s.in_[4]
            s.out[3] @= s.in_[6]

    TV_index = [IO(), (0b01010101, 0b1111), (0b10101010, 0b0000)]
    SV_index = (
        "  // s.out[0] @= s.in_[0]\n"
        "  assign __out_bits[32'h0 +: 1] = in_[0];\n"
        "  // s.out[1] @= s.in_[2]\n"
        "  assign __out_bits[32'h1 +: 1] = in_[2];\n"
        "  // s.out[2] @= s.in_[4]\n"
        "  assign __out_bits[32'h2 +: 1] = in_[4];\n"
        "  // s.out[3] @= s.in_[6]\n"
        "  assign __out_bits[32'h3 +: 1] = in_[6];"
    )

    def test_index(self):
        self.simulate(self.ConnectIndex(), self.TV_index)
        self.translate(self.ConnectIndex(), self.SV_index)

    class ConnectSlice(ConnectTarget):
        @build
        def connect(s):
            s.out[:2] @= s.in_[1:3]
            s.out[2:] @= s.in_[5:7]

    TV_slice = [IO(), (0b01010110, 0b1011), (0b10101001, 0b0100)]
    SV_slice = (
        "  // s.out[:2] @= s.in_[1:3]\n"
        "  assign __out_bits[32'h0 +: 2] = in_[2:1];\n"
        "  // s.out[2:] @= s.in_[5:7]\n"
        "  assign __out_bits[32'h2 +: 2] = in_[6:5];"
    )

    def test_slice(self):
        self.simulate(self.ConnectSlice(), self.TV_slice)
        self.translate(self.ConnectSlice(), self.SV_slice)

    class ConnectPartSel(ConnectTarget):
        @build
        def connect(s):
            s.out[0, 2] @= s.in_[1, 2]
            s.out[3, -2] @= s.in_[5, -2]

    TV_part_sel = [IO(), (0b01010110, 0b0111), (0b10101001, 0b1000)]
    SV_part_sel = (
        "  // s.out[0, 2] @= s.in_[1, 2]\n"
        "  assign __out_bits[32'h0 +: 2] = in_[32'h1 +: 2];\n"
        "  // s.out[3, -2] @= s.in_[5, -2]\n"
        "  assign __out_bits[32'h3 -: 2] = in_[32'h5 -: 2];"
    )

    def test_part_sel(self):
        self.simulate(self.ConnectPartSel(), self.TV_part_sel)
        self.translate(self.ConnectPartSel(), self.SV_part_sel)


class TestConnectConcatLHS(BaseTestCase):
    class ConcatConcatLHS(RawModule):
        @build
        def ports(s):
            s.in_data = Input(8)
            s.out_high = Output(4)
            s.out_low = Output(4)

        @build
        def connect_concat(s):
            cat(s.out_high, s.out_low)[:] @= s.in_data

    class IO(IOStruct):
        in_data = Input(8)
        out_high = Output(4)
        out_low = Output(4)

    TV_concat_comment = [
        IO(),
        (0xAB, 0xA, 0xB),
        (0xCD, 0xC, 0xD),
        (0x12, 0x1, 0x2),
        (0xFF, 0xF, 0xF),
    ]
    SV_concat_comment = (
        "  // cat(s.out_high, s.out_low)[:] @= s.in_data\n"
        "  assign __out_high_bits = in_data[7:4];\n"
        "  assign __out_low_bits = in_data[3:0];"
    )

    def test_concat_comment(self):
        self.simulate(self.ConcatConcatLHS(), self.TV_concat_comment)
        self.translate(self.ConcatConcatLHS(), self.SV_concat_comment)
