# Tests for HDL statement: assignments (/=, <<=)
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
    comb,
    seq,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestAssignValues(BaseTestCase):
    class ProceduralAssign(RawModule):
        @build
        def ports(s):
            s.clk = Input()
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

    class IO(IOStruct):
        clk = Input()
        in_scalar = Input()
        out_scalar = Output()
        in_vector = Input(4)
        out_vector = Output(4)
        out_bits = Output(8)
        out_int = Output(8)

    class BlockingAssign(ProceduralAssign):
        @comb
        def update_scalar(s):
            s.temp_scalar /= s.in_scalar
            s.out_scalar /= s.temp_scalar

        @comb
        def update_vector(s):
            s.temp_vector /= s.in_vector
            s.out_vector /= s.temp_vector

        @comb
        def update_const(s):
            s.out_bits /= b8(1) + b8(2) & b8(3)
            s.out_int /= 1 + 2 & 3

    TV_bassign = [
        IO(),
        (None, 0, 0, 0b0000, 0b0000, 0x03, 0x03),
        (None, 1, 1, 0b0101, 0b0101, 0x03, 0x03),
        (None, 0, 0, 0b1010, 0b1010, 0x03, 0x03),
        (None, 1, 1, 0b1111, 0b1111, 0x03, 0x03),
    ]
    SV_bassign = (
        "  // @comb update_scalar():\n"
        "  always_comb begin\n"
        "    temp_scalar = in_scalar;\n"
        "    __out_scalar_bits = temp_scalar;\n"
        "  end // always_comb\n"
        "\n"
        "  // @comb update_vector():\n"
        "  always_comb begin\n"
        "    temp_vector = in_vector;\n"
        "    __out_vector_bits = temp_vector;\n"
        "  end // always_comb\n"
        "\n"
        "  // @comb update_const():\n"
        "  always_comb begin\n"
        "    __out_bits_bits = 8'h1 + 8'h2 & 8'h3;\n"
        "    __out_int_bits = 8'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bassign(self):
        self.simulate(self.BlockingAssign(), self.TV_bassign)
        self.translate(self.BlockingAssign(), self.SV_bassign)

    class NonBlockingAssign(ProceduralAssign):
        @seq
        def update_scalar(s, posedge="clk"):
            s.temp_scalar <<= s.in_scalar
            s.out_scalar <<= s.temp_scalar

        @seq
        def update_vector(s, posedge="clk"):
            s.temp_vector <<= s.in_vector
            s.out_vector <<= s.temp_vector

        @seq
        def update_const(s, posedge="clk"):
            s.out_bits <<= b8(1) + b8(2) & b8(3)
            s.out_int <<= 1 + 2 & 3

    TV_nbassign = [
        IO(),
        (0, 1, None, 0b0101, None, None, None),
        (1, 1, None, 0b0101, None, 0x03, 0x03),
        (0, 1, None, 0b0101, None, 0x03, 0x03),
        (1, 1, 1, 0b0101, 0b0101, 0x03, 0x03),
        (0, 0, 1, 0b1010, 0b0101, 0x03, 0x03),
        (1, 0, 1, 0b1010, 0b0101, 0x03, 0x03),
        (0, 0, 1, 0b1010, 0b0101, 0x03, 0x03),
        (1, 0, 0, 0b1010, 0b1010, 0x03, 0x03),
    ]
    SV_nbassign = (
        "  // @seq update_scalar():\n"
        "  always @(posedge clk) begin\n"
        "    temp_scalar <= in_scalar;\n"
        "    __out_scalar_bits <= temp_scalar;\n"
        "  end // always @(posedge)\n"
        "\n"
        "  // @seq update_vector():\n"
        "  always @(posedge clk) begin\n"
        "    temp_vector <= in_vector;\n"
        "    __out_vector_bits <= temp_vector;\n"
        "  end // always @(posedge)\n"
        "\n"
        "  // @seq update_const():\n"
        "  always @(posedge clk) begin\n"
        "    __out_bits_bits <= 8'h1 + 8'h2 & 8'h3;\n"
        "    __out_int_bits <= 8'h3;\n"
        "  end // always @(posedge)\n"
        "\n"
    )

    def test_nbassign(self):
        self.simulate(self.NonBlockingAssign(), self.TV_nbassign)
        self.translate(self.NonBlockingAssign(), self.SV_nbassign)


class TestAssignConcatLHS(BaseTestCase):
    class ConcatCommentBA(RawModule):
        @build
        def ports(s):
            s.in_data = Input(8)
            s.out_high = Output(4)
            s.out_low = Output(4)

        @comb
        def assign_concat(s):
            cat(s.out_high, s.out_low)[:] /= s.in_data

    class IO(IOStruct):
        in_data = Input(8)
        out_high = Output(4)
        out_low = Output(4)

    TV_concat_comment_ba = [
        IO(),
        (0xAB, 0xA, 0xB),
        (0xCD, 0xC, 0xD),
        (0x12, 0x1, 0x2),
        (0xFF, 0xF, 0xF),
    ]
    SV_concat_comment_ba = (
        "  // @comb assign_concat():\n"
        "  always_comb begin\n"
        "    // cat(s.out_high, s.out_low)[:] /= s.in_data\n"
        "    __out_high_bits = in_data[7:4];\n"
        "    __out_low_bits = in_data[3:0];\n"
        "  end // always_comb\n"
    )

    def test_concat_comment(self):
        self.simulate(self.ConcatCommentBA(), self.TV_concat_comment_ba)
        self.translate(self.ConcatCommentBA(), self.SV_concat_comment_ba)
