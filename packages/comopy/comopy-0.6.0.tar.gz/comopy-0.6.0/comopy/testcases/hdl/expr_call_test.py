# Tests for HDL expression: function calls
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
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


# Bits properties
#

# Bits.V is tested in stmt_case_test.
# Bits.S is tested in expr_shift_test and expr_compare_test.


class TestBitsW(BaseTestCase):
    class BitsWidth(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(8)
        out = Output(8)

    class VecW(BitsWidth):
        @comb
        def update(s):
            s.out /= s.in_[s.in_.W - 1, -8]

    TV_vec = [IO(), (0x00, 0x00), (0xAB, 0xAB)]
    SV_vec = "    __out_bits = in_[$bits(in_) - 32'h1 -: 8];\n"

    def test_vec(self):
        self.simulate(self.VecW(), self.TV_vec)
        self.translate(self.VecW(), self.SV_vec)

    class BitsW(BitsWidth):
        @comb
        def update(s):
            s.out /= b4(0xF).W

    TV_bits = [IO(), (None, 4)]
    SV_bits = (
        "  always_comb begin\n"
        "    automatic logic [31:0] _GEN = $bits(4'hF);\n"
        "    __out_bits = _GEN[7:0];\n"
        "  end // always_comb\n"
    )

    def test_bits(self):
        self.simulate(self.BitsW(), self.TV_bits)
        self.translate(self.BitsW(), self.SV_bits)

    class ExprW(BitsWidth):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0xFF)).W

    TV_expr = [IO(), (0x00, 8), (0xAB, 8)]
    SV_expr = (
        "  always_comb begin\n"
        "    automatic logic [31:0] _GEN = $bits(in_ & 8'hFF);\n"
        "    __out_bits = _GEN[7:0];\n"
        "  end // always_comb\n"
    )

    def test_expr(self):
        self.simulate(self.ExprW(), self.TV_expr)
        self.translate(self.ExprW(), self.SV_expr)


class TestBitsN(BaseTestCase):
    class BitsWidth(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        out = Output()

    class VecN(BitsWidth):
        @comb
        def update(s):
            s.out /= s.in_.N

    TV_vec = [IO(), (0x00, 0), (0x80, 1), (0x7F, 0)]
    SV_vec = "    __out_bits = in_[$bits(in_) - 32'h1 +: 1];\n"

    def test_vec(self):
        self.simulate(self.VecN(), self.TV_vec)
        self.translate(self.VecN(), self.SV_vec)

    class BitsN(BitsWidth):
        @comb
        def update(s):
            s.out /= b4(0xF).N

    TV_bits = [IO(), (None, 1)]
    SV_bits = (
        "  always_comb begin\n"
        "    automatic logic [3:0] _GEN = 4'hF;\n"
        "    __out_bits = _GEN[$bits(_GEN) - 32'h1 +: 1];\n"
        "  end // always_comb\n"
    )

    def test_bits(self):
        self.simulate(self.BitsN(), self.TV_bits)
        self.translate(self.BitsN(), self.SV_bits)

    class ExprN(BitsWidth):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0xFF)).N

    TV_expr = [IO(), (0x00, 0), (0x80, 1), (0x7F, 0)]
    SV_expr = (
        "  always_comb begin\n"
        "    automatic logic [7:0] _GEN = in_ & 8'hFF;\n"
        "    __out_bits = _GEN[$bits(_GEN) - 32'h1 +: 1];\n"
        "  end // always_comb\n"
    )

    def test_expr(self):
        self.simulate(self.ExprN(), self.TV_expr)
        self.translate(self.ExprN(), self.SV_expr)


class TestBitsAO(BaseTestCase):
    class Reduce(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        out = Output()

    class VecAO(Reduce):
        @comb
        def update(s):
            s.out /= s.in_.AO

    TV_vec = [IO(), (0xAB, 0), (0xFF, 1)]
    SV_vec = "    __out_bits = &in_;\n"

    def test_vec(self):
        self.simulate(self.VecAO(), self.TV_vec)
        self.translate(self.VecAO(), self.SV_vec)

    class BitsAO(Reduce):
        @comb
        def update(s):
            s.out /= (b4(0xF) ^ b4(0xB)).AO

    TV_bits = [IO(), (None, 0)]
    SV_bits = "    __out_bits = &(4'hF ^ 4'hB);\n"

    def test_bits(self):
        self.simulate(self.BitsAO(), self.TV_bits)
        self.translate(self.BitsAO(), self.SV_bits)

    class ExprAO(Reduce):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0xFF)).AO

    TV_expr = [IO(), (0xAB, 0), (0xFF, 1)]
    SV_expr = "    __out_bits = &(in_ & 8'hFF);\n"

    def test_expr(self):
        self.simulate(self.ExprAO(), self.TV_expr)
        self.translate(self.ExprAO(), self.SV_expr)


class TestBitsNZ(BaseTestCase):
    class Reduce(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        out = Output()

    class VecNZ(Reduce):
        @comb
        def update(s):
            s.out /= s.in_.NZ

    TV_vec = [IO(), (0x00, 0), (0xAB, 1)]
    SV_vec = "    __out_bits = |in_;\n"

    def test_vec(self):
        self.simulate(self.VecNZ(), self.TV_vec)
        self.translate(self.VecNZ(), self.SV_vec)

    class BitsNZ(Reduce):
        @comb
        def update(s):
            s.out /= (b4(0xF) & b4(0x0)).NZ

    TV_bits = [IO(), (None, 0)]
    SV_bits = "    __out_bits = |(4'hF & 4'h0);\n"

    def test_bits(self):
        self.simulate(self.BitsNZ(), self.TV_bits)
        self.translate(self.BitsNZ(), self.SV_bits)

    class ExprNZ(Reduce):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0xFF)).NZ

    TV_expr = [IO(), (0x00, 0), (0xAB, 1)]
    SV_expr = "    __out_bits = |(in_ & 8'hFF);\n"

    def test_expr(self):
        self.simulate(self.ExprNZ(), self.TV_expr)
        self.translate(self.ExprNZ(), self.SV_expr)


class TestBitsP(BaseTestCase):
    class Reduce(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        out = Output()

    class VecP(Reduce):
        @comb
        def update(s):
            s.out /= s.in_.P

    TV_vec = [IO(), (0x00, 0), (0x03, 0), (0x07, 1), (0xFF, 0)]
    SV_vec = "    __out_bits = ^in_;\n"

    def test_vec(self):
        self.simulate(self.VecP(), self.TV_vec)
        self.translate(self.VecP(), self.SV_vec)

    class BitsP(Reduce):
        @comb
        def update(s):
            s.out /= (b4(0xF) & b4(0x6)).P

    TV_bits = [IO(), (None, 0)]
    SV_bits = "    __out_bits = ^(4'hF & 4'h6);\n"

    def test_bits(self):
        self.simulate(self.BitsP(), self.TV_bits)
        self.translate(self.BitsP(), self.SV_bits)

    class ExprP(Reduce):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0x0F)).P

    TV_expr = [IO(), (0x00, 0), (0xF7, 1), (0x0F, 0)]
    SV_expr = "    __out_bits = ^(in_ & 8'hF);\n"

    def test_expr(self):
        self.simulate(self.ExprP(), self.TV_expr)
        self.translate(self.ExprP(), self.SV_expr)


class TestBitsZ(BaseTestCase):
    class Reduce(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        out = Output()

    class VecZ(Reduce):
        @comb
        def update(s):
            s.out /= s.in_.Z

    TV_vec = [IO(), (0x00, 1), (0xAB, 0)]
    SV_vec = "    __out_bits = in_ == 8'h0;\n"

    def test_vec(self):
        self.simulate(self.VecZ(), self.TV_vec)
        self.translate(self.VecZ(), self.SV_vec)

    class BitsZ(Reduce):
        @comb
        def update(s):
            s.out /= (b4(0xF) & b4(0x0)).Z

    TV_bits = [IO(), (None, 1)]
    SV_bits = "    __out_bits = (4'hF & 4'h0) == 4'h0;\n"

    def test_bits(self):
        self.simulate(self.BitsZ(), self.TV_bits)
        self.translate(self.BitsZ(), self.SV_bits)

    class ExprZ(Reduce):
        @comb
        def update(s):
            s.out /= (s.in_ & b8(0xFF)).Z

    TV_expr = [IO(), (0x00, 1), (0xAB, 0)]
    SV_expr = "    __out_bits = (in_ & 8'hFF) == 8'h0;\n"

    def test_expr(self):
        self.simulate(self.ExprZ(), self.TV_expr)
        self.translate(self.ExprZ(), self.SV_expr)


# Function calls
#
class TestBitsConstructor(BaseTestCase):
    class bN(RawModule):
        @build
        def build_all(s):
            s.out = Output(8)

    class IO(IOStruct):
        out = Output(8)

    class ByInt(bN):
        @comb
        def update(s):
            s.out /= b8(0xAB)

    TV_by_int = [IO(), (0xAB,)]
    SV_by_int = "    __out_bits = 8'hAB;\n"

    def test_by_int(self):
        self.simulate(self.ByInt(), self.TV_by_int)
        self.translate(self.ByInt(), self.SV_by_int)

    class ByIntExpr(bN):
        @comb
        def update(s):
            s.out /= b8(0x50 + 0x5B)

    TV_by_int_expr = [IO(), (0xAB,)]
    SV_by_int_expr = "    __out_bits = 8'hAB;\n"

    def test_by_int_expr(self):
        self.simulate(self.ByIntExpr(), self.TV_by_int_expr)
        self.translate(self.ByIntExpr(), self.SV_by_int_expr)


# Bool() is tested in expr_boolean_test.


class TestExtension(BaseTestCase):
    class Ext(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(4)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(4)
        out = Output(8)

    class ZeroExt(Ext):
        @comb
        def update(s):
            s.out /= s.in_.ext(8)

    TV_zext = [IO(), (0xA, 0x0A), (0xF, 0x0F)]
    SV_zext = "    __out_bits = {4'h0, in_};\n"

    def test_zext(self):
        self.simulate(self.ZeroExt(), self.TV_zext)
        self.translate(self.ZeroExt(), self.SV_zext)

    class ZeroExtExpr(Ext):
        @comb
        def update(s):
            s.out /= (s.in_ & b4(0x3)).ext(8)

    TV_zext_expr = [IO(), (0xA, 0x02), (0xF, 0x03)]
    SV_zext_expr = "    __out_bits = {4'h0, in_ & 4'h3};\n"

    def test_zext_expr(self):
        self.simulate(self.ZeroExtExpr(), self.TV_zext_expr)
        self.translate(self.ZeroExtExpr(), self.SV_zext_expr)

    class SignedExt(Ext):
        @comb
        def update(s):
            s.out /= s.in_.S.ext(8)

    TV_sext = [IO(), (0x5, 0x05), (0xA, 0xFA), (0xF, 0xFF)]
    SV_sext = "    __out_bits = {{4{in_[3]}}, in_};\n"

    def test_sext(self):
        self.simulate(self.SignedExt(), self.TV_sext)
        self.translate(self.SignedExt(), self.SV_sext)

    class NestedExt(Ext):
        @comb
        def update(s):
            s.out /= s.in_.S.ext(6).ext(8)

    TV_nested = [IO(), (0x5, 0x05), (0xA, 0x3A), (0xF, 0x3F)]
    SV_nested = "    __out_bits = {2'h0, {{2{in_[3]}}, in_}};\n"

    def test_nested(self):
        self.simulate(self.NestedExt(), self.TV_nested)
        self.translate(self.NestedExt(), self.SV_nested)
