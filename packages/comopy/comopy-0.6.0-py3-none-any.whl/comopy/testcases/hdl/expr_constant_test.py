# Tests for HDL expression: constants
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    IOStruct,
    Output,
    RawModule,
    build,
    comb,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestConnectInt(BaseTestCase):
    class IntConst(RawModule):
        @build
        def ports(s):
            s.out = Output(8)

    class IO(IOStruct):
        out = Output(8)

    class ConnectInt(IntConst):
        @build
        def connect(s):
            s.out @= 0

    TV_int = [IO(), (0,)]
    SV_int = "  assign __out_bits = 8'h0;"

    def test_int(self):
        self.simulate(self.ConnectInt(), self.TV_int)
        self.translate(self.ConnectInt(), self.SV_int)

    class ConnectIntMax(IntConst):
        @build
        def connect(s):
            s.out @= 255

    TV_int_max = [IO(), (255,)]  # 255 = 0xFF for 8 bits max
    SV_int_max = "  assign __out_bits = 8'hFF;"

    def test_int_max(self):
        self.simulate(self.ConnectIntMax(), self.TV_int_max)
        self.translate(self.ConnectIntMax(), self.SV_int_max)

    class ConnectIntMin(IntConst):
        @build
        def connect(s):
            s.out @= -128

    TV_int_min = [IO(), (128,)]  # -128 = 0x80 for 8 bits min
    SV_int_min = "  assign __out_bits = 8'h80;"

    def test_int_min(self):
        self.simulate(self.ConnectIntMin(), self.TV_int_min)
        self.translate(self.ConnectIntMin(), self.SV_int_min)

    class ConnectInvert(IntConst):
        @build
        def connect(s):
            s.out @= ~0x21

    TV_invert = [IO(), (0xDE,)]  # ~0x21 = 0xDE
    SV_invert = "  assign __out_bits = 8'hDE;"

    def test_invert(self):
        self.simulate(self.ConnectInvert(), self.TV_invert)
        self.translate(self.ConnectInvert(), self.SV_invert)

    class ConnectUAdd(IntConst):
        @build
        def connect(s):
            s.out @= +0x21

    TV_uadd = [IO(), (0x21,)]  # +0x21 = 0x21
    SV_uadd = "  assign __out_bits = 8'h21;"

    def test_uadd(self):
        self.simulate(self.ConnectUAdd(), self.TV_uadd)
        self.translate(self.ConnectUAdd(), self.SV_uadd)

    class ConnectUSub(IntConst):
        @build
        def connect(s):
            s.out @= -1

    TV_usub = [IO(), (0xFF,)]  # -1 = 0xFF for 8 bits
    SV_usub = "  assign __out_bits = 8'hFF;"

    def test_usub(self):
        self.simulate(self.ConnectUSub(), self.TV_usub)
        self.translate(self.ConnectUSub(), self.SV_usub)

    class ConnectIntOpBits(IntConst):
        @build
        def connect(s):
            s.out @= 0x12 | b8(0)

    TV_int_op_bits = [IO(), (0x12,)]
    SV_int_op_bits = "  assign __out_bits = 8'h12 | 8'h0;"

    def test_int_op_bits(self):
        self.simulate(self.ConnectIntOpBits(), self.TV_int_op_bits)
        self.translate(self.ConnectIntOpBits(), self.SV_int_op_bits)

    class ConnectBitsOpInt(IntConst):
        @build
        def connect(s):
            s.out @= b8(1) | 0x34

    TV_bits_op_int = [IO(), (0x35,)]
    SV_bits_op_int = "  assign __out_bits = 8'h1 | 8'h34;"

    def test_bits_op_int(self):
        self.simulate(self.ConnectBitsOpInt(), self.TV_bits_op_int)
        self.translate(self.ConnectBitsOpInt(), self.SV_bits_op_int)

    class ConnectBoolInt(IntConst):
        @build
        def connect(s):
            s.out @= rep(8, Bool(0xAB))

    TV_bool = [IO(), (0xFF,)]
    SV_bool_int = "  assign __out_bits = {8{1'h1}};"

    def test_bool_int(self):
        self.simulate(self.ConnectBoolInt(), self.TV_bool)
        self.translate(self.ConnectBoolInt(), self.SV_bool_int)

    class ConnectBoolNot(IntConst):
        @build
        def connect(s):
            s.out[1:] @= 0
            s.out[0] @= not 0xAB

    TV_bool_not = [IO(), (0x0,)]
    SV_bool_not = (
        "  // s.out[1:] @= 0\n"
        "  assign __out_bits[32'h1 +: 7] = 7'h0;\n"
        "  // s.out[0] @= not 0xAB\n"
        "  assign __out_bits[32'h0 +: 1] = 1'h0;\n"
    )

    def test_bool_not(self):
        self.simulate(self.ConnectBoolNot(), self.TV_bool_not)
        self.translate(self.ConnectBoolNot(), self.SV_bool_not)

    class ConnectBoolOr(IntConst):
        @build
        def connect(s):
            s.out[1:] @= 0
            s.out[0] @= Bool(0x12 or b8(0))

    TV_bool_or = [IO(), (0x1,)]
    SV_bool_or = (
        "  // s.out[1:] @= 0\n"
        "  assign __out_bits[32'h1 +: 7] = 7'h0;\n"
        "  // s.out[0] @= Bool(0x12 or b8(0))\n"
        "  assign __out_bits[32'h0 +: 1] = (|(32'h12)) | (|(8'h0));\n"
    )

    def test_bool_or(self):
        self.simulate(self.ConnectBoolOr(), self.TV_bool_or)
        self.translate(self.ConnectBoolOr(), self.SV_bool_or)


class TestAssignInt(BaseTestCase):
    class IntConst(RawModule):
        @build
        def ports(s):
            s.out = Output(8)

    class IO(IOStruct):
        out = Output(8)

    class AssignInt(IntConst):
        @comb
        def update(s):
            s.out /= 0

    TV_int = [IO(), (0,)]
    SV_int = "    __out_bits = 8'h0;"

    def test_int(self):
        self.simulate(self.AssignInt(), self.TV_int)
        self.translate(self.AssignInt(), self.SV_int)

    class AssignIntMax(IntConst):
        @comb
        def update(s):
            s.out /= 255

    TV_int_max = [IO(), (255,)]  # 255 = 0xFF for 8 bits max
    SV_int_max = "    __out_bits = 8'hFF;"

    def test_int_max(self):
        self.simulate(self.AssignIntMax(), self.TV_int_max)
        self.translate(self.AssignIntMax(), self.SV_int_max)

    class AssignIntMin(IntConst):
        @comb
        def update(s):
            s.out /= -128

    TV_int_min = [IO(), (-128,)]  # -128 = 0x80 for 8 bits min
    SV_int_min = "    __out_bits = 8'h80;"

    def test_int_min(self):
        self.simulate(self.AssignIntMin(), self.TV_int_min)
        self.translate(self.AssignIntMin(), self.SV_int_min)

    class AssignInvert(IntConst):
        @comb
        def update(s):
            s.out /= ~0x21

    TV_invert = [IO(), (0xDE,)]  # ~0x21 = 0xDE
    SV_invert = "    __out_bits = 8'hDE;"

    def test_invert(self):
        self.simulate(self.AssignInvert(), self.TV_invert)
        self.translate(self.AssignInvert(), self.SV_invert)

    class AssignUAdd(IntConst):
        @comb
        def update(s):
            s.out /= +0x21

    TV_uadd = [IO(), (0x21,)]  # +0x21 = 0x21
    SV_uadd = "    __out_bits = 8'h21;"

    def test_uadd(self):
        self.simulate(self.AssignUAdd(), self.TV_uadd)
        self.translate(self.AssignUAdd(), self.SV_uadd)

    class AssignUSub(IntConst):
        @comb
        def update(s):
            s.out /= -1

    TV_usub = [IO(), (0xFF,)]  # -1 = 0xFF for 8 bits
    SV_usub = "    __out_bits = 8'hFF;"

    def test_usub(self):
        self.simulate(self.AssignUSub(), self.TV_usub)
        self.translate(self.AssignUSub(), self.SV_usub)

    class AssignIntOpBits(IntConst):
        @comb
        def update(s):
            s.out /= 0x12 | b8(0)

    TV_int_op_bits = [IO(), (0x12,)]
    SV_int_op_bits = "    __out_bits = 8'h12 | 8'h0;"

    def test_int_op_bits(self):
        self.simulate(self.AssignIntOpBits(), self.TV_int_op_bits)
        self.translate(self.AssignIntOpBits(), self.SV_int_op_bits)

    class AssignBitsOpInt(IntConst):
        @comb
        def update(s):
            s.out /= b8(1) | 0x34

    TV_bits_op_int = [IO(), (0x35,)]
    SV_bits_op_int = "    __out_bits = 8'h1 | 8'h34;"

    def test_bits_op_int(self):
        self.simulate(self.AssignBitsOpInt(), self.TV_bits_op_int)
        self.translate(self.AssignBitsOpInt(), self.SV_bits_op_int)

    class AssignBoolInt(IntConst):
        @comb
        def update(s):
            s.out /= rep(8, Bool(0xAB))

    TV_bool_int = [IO(), (0xFF,)]
    SV_bool_int = "    __out_bits = {8{1'h1}};"

    def test_bool_int(self):
        self.simulate(self.AssignBoolInt(), self.TV_bool_int)
        self.translate(self.AssignBoolInt(), self.SV_bool_int)

    class AssignBoolNot(IntConst):
        @comb
        def update(s):
            s.out[1:] /= 0
            s.out[0] /= not 0xAB

    TV_bool_not = [IO(), (0x0,)]
    SV_bool_not = (
        "    // s.out[1:] /= 0\n"
        "    __out_bits[32'h1 +: 7] = 7'h0;\n"
        "    // s.out[0] /= not 0xAB\n"
        "    __out_bits[32'h0 +: 1] = 1'h0;\n"
    )

    def test_bool_not(self):
        self.simulate(self.AssignBoolNot(), self.TV_bool_not)
        self.translate(self.AssignBoolNot(), self.SV_bool_not)

    class AssignBoolOr(IntConst):
        @comb
        def update(s):
            s.out[1:] /= 0
            s.out[0] /= Bool(0x12 or b8(0))

    TV_bool_or = [IO(), (0x1,)]
    SV_bool_or = (
        "    // s.out[1:] /= 0\n"
        "    __out_bits[32'h1 +: 7] = 7'h0;\n"
        "    // s.out[0] /= Bool(0x12 or b8(0))\n"
        "    __out_bits[32'h0 +: 1] = (|(32'h12)) | (|(8'h0));\n"
    )

    def test_bool_or(self):
        self.simulate(self.AssignBoolOr(), self.TV_bool_or)
        self.translate(self.AssignBoolOr(), self.SV_bool_or)


class TestBoolConst(BaseTestCase):
    class BoolConst(RawModule):
        @build
        def ports(s):
            s.out0 = Output()
            s.out1 = Output()

    class IO(IOStruct):
        out0 = Output()
        out1 = Output()

    TV = [IO(), (0, 0)]

    class ConnectBoolConst(BoolConst):
        @build
        def connect(s):
            s.out0 @= FALSE
            s.out1 @= ~TRUE

    SV_connect = (
        "  // Variables for output ports\n"
        "  logic __out0_bits;\n"
        "  logic __out1_bits;\n"
        "\n"
        "  assign __out0_bits = 1'h0;\n"
        "  assign __out1_bits = ~(1'h1);\n"
    )

    def test_connect(self):
        self.simulate(self.ConnectBoolConst(), self.TV)
        self.translate(self.ConnectBoolConst(), self.SV_connect)

    class AssignBoolConst(BoolConst):
        @comb
        def update(s):
            s.out0 /= FALSE
            s.out1 /= ~TRUE

    SV_assign = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out0_bits = 1'h0;\n"
        "    __out1_bits = ~(1'h1);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_assign(self):
        self.simulate(self.AssignBoolConst(), self.TV)
        self.translate(self.AssignBoolConst(), self.SV_assign)
