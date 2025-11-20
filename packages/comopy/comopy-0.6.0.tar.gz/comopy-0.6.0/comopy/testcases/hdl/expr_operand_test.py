# Tests for HDL expression: operands
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
)
from comopy.bits import b8  # type: ignore


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestAttr(BaseTestCase):
    class Attr(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(8)
        out = Output(8)

    class InOutPorts(Attr):
        @comb
        def update(self):
            self.out /= self.in_

    TV_ports = [IO(), (0xAB, 0xAB)]
    SV_ports = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in_;\n"
        "\n"
    )

    def test_ports(self):
        self.simulate(self.InOutPorts(), self.TV_ports)
        self.translate(self.InOutPorts(), self.SV_ports)

    class LogicAttr(Attr):
        @build
        def build_logic(s):
            s.temp = Logic(8)

        @comb
        def update(self):
            self.temp /= self.in_
            self.out /= self.temp

    TV_logic = [IO(), (0xAB, 0xAB)]
    SV_logic = (
        "  logic [7:0] temp;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    temp = in_;\n"
        "    __out_bits = temp;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_logic(self):
        self.simulate(self.LogicAttr(), self.TV_logic)
        self.translate(self.LogicAttr(), self.SV_logic)


CONST_INT = 123
CONST_WIDTH = 16
CONST_BITS = b8(0x80)


class TestGlobalInt(BaseTestCase):
    class GlobalConst(RawModule):
        @build
        def ports(s):
            s.out1 = Output(16)
            s.out2 = Output(16)

    class IO(IOStruct):
        out1 = Output(16)
        out2 = Output(16)

    class ConnI32(GlobalConst):
        @build
        def assign(s):
            s.out1 @= CONST_INT
            s.out2 @= CONST_INT

    TV_conn_i32 = [IO(), (123, 123)]
    SV_conn_i32 = (
        "  // Local parameters\n"
        "  localparam [31:0] CONST_INT = 123;\n"
        "\n"
        "  assign __out1_bits = CONST_INT[15:0];\n"
        "  assign __out2_bits = CONST_INT[15:0];\n"
    )

    def test_conn_i32(self):
        self.simulate(self.ConnI32(), self.TV_conn_i32)
        self.translate(self.ConnI32(), self.SV_conn_i32)

    class ConnI32Expr(GlobalConst):
        @build
        def assign(s):
            s.out1 @= CONST_INT + 1
            s.out2 @= CONST_INT - 1

    TV_conn_i32_expr = [IO(), (124, 122)]
    SV_conn_i32_expr = (
        "  // Local parameters\n"
        "  localparam [31:0] CONST_INT = 123;\n"
        "\n"
        "  wire       [31:0] _GEN = CONST_INT + 32'h1;\n"
        "  assign __out1_bits = _GEN[15:0];\n"
        "  wire       [31:0] _GEN_0 = CONST_INT - 32'h1;\n"
        "  assign __out2_bits = _GEN_0[15:0];\n"
    )

    def test_conn_i32_expr(self):
        self.simulate(self.ConnI32Expr(), self.TV_conn_i32_expr)
        self.translate(self.ConnI32Expr(), self.SV_conn_i32_expr)

    class CombI32(GlobalConst):
        @comb
        def update(s):
            s.out1 /= CONST_INT
            s.out2 /= CONST_INT

    TV_comb_i32 = [IO(), (123, 123)]
    SV_comb_i32 = (
        "  // Local parameters\n"
        "  localparam [31:0] CONST_INT = 123;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = CONST_INT[15:0];\n"
        "    __out2_bits = CONST_INT[15:0];\n"
        "  end // always_comb\n"
    )

    def test_comb_i32(self):
        self.simulate(self.CombI32(), self.TV_comb_i32)
        self.translate(self.CombI32(), self.SV_comb_i32)

    class CombI32Expr(GlobalConst):
        @comb
        def update(s):
            s.out1 /= CONST_INT + 1
            s.out2 /= CONST_INT - 1

    TV_comb_i32_expr = [IO(), (124, 122)]
    SV_comb_i32_expr = (
        "  // Local parameters\n"
        "  localparam [31:0] CONST_INT = 123;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    automatic logic [31:0] _GEN = CONST_INT + 32'h1;\n"
        "    automatic logic [31:0] _GEN_0 = CONST_INT - 32'h1;\n"
        "    __out1_bits = _GEN[15:0];\n"
        "    __out2_bits = _GEN_0[15:0];\n"
        "  end // always_comb\n"
    )

    def test_comb_i32_expr(self):
        self.simulate(self.CombI32Expr(), self.TV_comb_i32_expr)
        self.translate(self.CombI32Expr(), self.SV_comb_i32_expr)

    class I32ExprIndex(GlobalConst):
        @comb
        def update(s):
            s.out1 /= 0
            s.out2 /= 0
            s.out1[CONST_WIDTH - 1, -8] /= 0xAB
            s.out2[: CONST_WIDTH >> 1] /= 0x12

    TV_i32_expr_index = [IO(), (0xAB00, 0x0012)]
    SV_i32_expr_index = (
        "  // Local parameters\n"
        "  localparam [31:0] CONST_WIDTH = 16;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 16'h0;\n"
        "    __out2_bits = 16'h0;\n"
        "    // s.out1[CONST_WIDTH - 1, -8] /= 0xAB\n"
        "    __out1_bits[CONST_WIDTH - 32'h1 -: 8] = 8'hAB;\n"
        "    // s.out2[: CONST_WIDTH >> 1] /= 0x12\n"
        "    __out2_bits[32'h0 +: 8] = 8'h12;\n"
        "  end // always_comb\n"
    )

    def test_i32_expr_index(self):
        self.simulate(self.I32ExprIndex(), self.TV_i32_expr_index)
        self.translate(self.I32ExprIndex(), self.SV_i32_expr_index)


class TestGlobalBits(BaseTestCase):
    class GlobalConst(RawModule):
        @build
        def ports(s):
            s.out1 = Output(16)
            s.out2 = Output(16)

    class IO(IOStruct):
        out1 = Output(16)
        out2 = Output(16)

    class ConnBitsExpr(GlobalConst):
        @build
        def assign(s):
            s.out1 @= cat(b8(0), CONST_BITS)
            s.out2 @= cat(CONST_BITS, b8(0))

    TV_conn_bits_expr = [IO(), (0x80, 0x8000)]
    SV_conn_bits_expr = (
        "  // Variables for output ports\n"
        "  logic      [15:0] __out1_bits;\n"
        "  logic      [15:0] __out2_bits;\n"
        "\n"
        "  // Local parameters\n"
        "  localparam [7:0]  CONST_BITS = 128;\n"
        "\n"
        "  assign __out1_bits = {8'h0, CONST_BITS};\n"
        "  assign __out2_bits = {CONST_BITS, 8'h0};\n"
    )

    def test_conn_bits_expr(self):
        self.simulate(self.ConnBitsExpr(), self.TV_conn_bits_expr)
        self.translate(self.ConnBitsExpr(), self.SV_conn_bits_expr)
