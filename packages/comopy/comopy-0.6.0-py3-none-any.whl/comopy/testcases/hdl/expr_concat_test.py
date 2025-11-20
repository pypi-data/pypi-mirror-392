# Tests for HDL expression: concatenation and replication
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


class TestConcatRHS(BaseTestCase):
    class Concat(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in2 = Input(2)
            s.in4 = Input(4)
            s.in8 = Input(8)
            s.out = Output(16)

    class IO(IOStruct):
        in1 = Input()
        in2 = Input(2)
        in4 = Input(4)
        in8 = Input(8)
        out = Output(16)

    class ConcatVec(Concat):
        @comb
        def update(s):
            s.out /= cat(s.in1, s.in2, s.in1, s.in4, s.in8)

    TV_vec = [IO(), (0, 0b11, 0xA, 0xCD, 0x6ACD)]
    SV_vec = "    __out_bits = {in1, in2, in1, in4, in8};\n"

    def test_vec(self):
        self.simulate(self.ConcatVec(), self.TV_vec)
        self.translate(self.ConcatVec(), self.SV_vec)

    class ConcatBits(Concat):
        @comb
        def update(s):
            s.out /= cat(b4(0xA), s.in8, b4(0xB))

    TV_bits = [IO(), (None, None, None, 0xCD, 0xACDB)]
    SV_bits = "    __out_bits = {4'hA, in8, 4'hB};\n"

    def test_bits(self):
        self.simulate(self.ConcatBits(), self.TV_bits)
        self.translate(self.ConcatBits(), self.SV_bits)

    class ConcatExpr(Concat):
        @comb
        def update(s):
            s.out /= cat(
                s.in4 & b4(0xF), s.in8 | b8(0xF), s.in2 ^ b2(0x3), s.in2
            )

    TV_expr = [IO(), (None, 0b11, 0xA, 0xCD, 0xACF3)]
    SV_expr = "    __out_bits = {in4 & 4'hF, in8 | 8'hF, ~in2, in2};\n"

    def test_expr(self):
        self.simulate(self.ConcatExpr(), self.TV_expr)
        self.translate(self.ConcatExpr(), self.SV_expr)

    class Nested(Concat):
        @comb
        def update(s):
            s.out /= cat(
                cat(s.in1, s.in2, ~s.in1), s.in4, cat(s.in8[:4], s.in8[4:])
            )

    TV_nested = [IO(), (1, 0b11, 0xA, 0xCD, 0xEADC)]
    SV_nested = (
        "    __out_bits = {{in1, in2, ~in1}, in4, {in8[3:0], in8[7:4]}};\n"
    )

    def test_nested(self):
        self.simulate(self.Nested(), self.TV_nested)
        self.translate(self.Nested(), self.SV_nested)


class TestConcatLHS(BaseTestCase):
    class AssignConcat(RawModule):
        @build
        def ports(s):
            s.a = Input(4)
            s.b = Input(4)
            s.c = Input(4)
            s.d = Input(4)
            s.o1 = Output(8)
            s.o2 = Output(8)

    class IO(IOStruct):
        a = Input(4)
        b = Input(4)
        c = Input(4)
        d = Input(4)
        o1 = Output(8)
        o2 = Output(8)

    class ConcatVec(AssignConcat):
        @comb
        def update(s):
            cat(s.o1, s.o2)[:] /= cat(s.a, s.b, s.c, s.d)

    TV_vec = [IO(), (0xA, 0xB, 0xC, 0xD, 0xAB, 0xCD)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    automatic logic [15:0] _GEN = {a, b, c, d};\n"
        "    // cat(s.o1, s.o2)[:] /= cat(s.a, s.b, s.c, s.d)\n"
        "    __o1_bits = _GEN[15:8];\n"
        "    __o2_bits = _GEN[7:0];\n"
        "  end // always_comb"
    )

    def test_vec(self):
        self.simulate(self.ConcatVec(), self.TV_vec)
        self.translate(self.ConcatVec(), self.SV_vec)

    class ConcatSlice(AssignConcat):
        @comb
        def update(s):
            cat(s.o1[:4], s.o2[:4], s.o1[4:], s.o2[4:])[:] /= cat(
                s.a, s.b, s.c, s.d
            )

    TV_slice = [IO(), (0xA, 0xB, 0xC, 0xD, 0xCA, 0xDB)]
    SV_slice = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    automatic logic [15:0] _GEN = {a, b, c, d};\n"
        "    // cat(s.o1[:4], s.o2[:4], s.o1[4:], s.o2[4:])[:] /= cat(\n"
        "    //     s.a, s.b, s.c, s.d\n"
        "    // )\n"
        "    __o1_bits[32'h0 +: 4] = _GEN[15:12];\n"
        "    __o2_bits[32'h0 +: 4] = _GEN[11:8];\n"
        "    __o1_bits[32'h4 +: 4] = _GEN[7:4];\n"
        "    __o2_bits[32'h4 +: 4] = _GEN[3:0];\n"
        "  end // always_comb"
    )

    def test_slice(self):
        self.simulate(self.ConcatSlice(), self.TV_slice)
        self.translate(self.ConcatSlice(), self.SV_slice)

    class Nested(AssignConcat):
        @comb
        def update(s):
            cat(cat(s.o1[:4], s.o2[:4]), cat(s.o1[4:], s.o2[4:]))[:] /= cat(
                s.a, cat(s.b, s.c), s.d
            )

    TV_nested = [IO(), (0xA, 0xB, 0xC, 0xD, 0xCA, 0xDB)]
    SV_nested = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    automatic logic [15:0] _GEN = {a, {b, c}, d};\n"
        "    automatic logic [7:0]  _GEN_0 = _GEN[15:8];\n"
        "    automatic logic [7:0]  _GEN_1 = _GEN[7:0];\n"
        "    // cat(cat(s.o1[:4], s.o2[:4]), cat(s.o1[4:], s.o2[4:]))[:] "
        "/= cat(\n"
        "    //     s.a, cat(s.b, s.c), s.d\n"
        "    // )\n"
        "    __o1_bits[32'h0 +: 4] = _GEN_0[7:4];\n"
        "    __o2_bits[32'h0 +: 4] = _GEN_0[3:0];\n"
        "    __o1_bits[32'h4 +: 4] = _GEN_1[7:4];\n"
        "    __o2_bits[32'h4 +: 4] = _GEN_1[3:0];\n"
        "  end // always_comb"
    )

    def test_nested(self):
        self.simulate(self.Nested(), self.TV_nested)
        self.translate(self.Nested(), self.SV_nested)


class TestReplicate(BaseTestCase):
    class Replicate(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in2 = Input(2)
            s.in4 = Input(4)
            s.in8 = Input(8)
            s.out = Output(16)

    class IO(IOStruct):
        in1 = Input()
        in2 = Input(2)
        in4 = Input(4)
        in8 = Input(8)
        out = Output(16)

    class RepVec(Replicate):
        @comb
        def update(s):
            s.out /= rep(2, s.in8)

    TV_vec = [IO(), (None, None, None, 0xCD, 0xCDCD)]
    SV_vec = "    __out_bits = {2{in8}};\n"

    def test_vec(self):
        self.simulate(self.RepVec(), self.TV_vec)
        self.translate(self.RepVec(), self.SV_vec)

    class RepVecCountIntExpr(Replicate):
        @comb
        def update(s):
            s.out /= rep(2 + 2 & 0xF, s.in4)

    TV_vec_count_int_expr = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_vec_count_int_expr = "    __out_bits = {4{in4}};\n"

    def test_vec_count_int_expr(self):
        self.simulate(self.RepVecCountIntExpr(), self.TV_vec_count_int_expr)
        self.translate(self.RepVecCountIntExpr(), self.SV_vec_count_int_expr)

    class RepBits(Replicate):
        @comb
        def update(s):
            s.out /= rep(4, b4(0xA))

    TV_bits = [IO(), (None, None, None, None, 0xAAAA)]
    SV_bits = "    __out_bits = {4{4'hA}};\n"

    def test_bits(self):
        self.simulate(self.RepBits(), self.TV_bits)
        self.translate(self.RepBits(), self.SV_bits)

    class RepExpr(Replicate):
        @comb
        def update(s):
            s.out /= cat(rep(3, s.in4 & b4(0xF)), s.in8[2:6] | 0)

    TV_expr = [IO(), (None, None, 0xA, 0xF0, 0xAAAC)]
    SV_expr = "    __out_bits = {{3{in4 & 4'hF}}, in8[5:2] | 4'h0};\n"

    def test_expr(self):
        self.simulate(self.RepExpr(), self.TV_expr)
        self.translate(self.RepExpr(), self.SV_expr)

    class RepNested(Replicate):
        @comb
        def update(s):
            s.out /= rep(2, rep(2, s.in4))

    TV_nested = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_nested = "    __out_bits = {2{{2{in4}}}};\n"

    def test_nested(self):
        self.simulate(self.RepNested(), self.TV_nested)
        self.translate(self.RepNested(), self.SV_nested)

    class RepMultiVec(Replicate):
        @comb
        def update(s):
            s.out /= rep(4, s.in1, s.in2, s.in1)

    TV_multi_vec = [IO(), (1, 0b00, None, None, 0x9999)]
    SV_multi_vec = "    __out_bits = {4{in1, in2, in1}};\n"

    def test_multi_vec(self):
        self.simulate(self.RepMultiVec(), self.TV_multi_vec)
        self.translate(self.RepMultiVec(), self.SV_multi_vec)

    class RepMultiBits(Replicate):
        @comb
        def update(s):
            s.out /= rep(1, b4(0xA), b4(0xB), b4(0xC), b4(0xD))

    TV_multi_bits = [IO(), (None, None, None, None, 0xABCD)]
    SV_multi_bits = "    __out_bits = {1{4'hA, 4'hB, 4'hC, 4'hD}};\n"

    def test_multi_bits(self):
        self.simulate(self.RepMultiBits(), self.TV_multi_bits)
        self.translate(self.RepMultiBits(), self.SV_multi_bits)

    class RepMultiExpr(Replicate):
        @comb
        def update(s):
            s.out /= rep(2, s.in4 & b4(0xF), s.in4 | b4(0x0))

    TV_multi_expr = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_multi_expr = "    __out_bits = {2{in4 & 4'hF, in4 | 4'h0}};\n"

    def test_multi_expr(self):
        self.simulate(self.RepMultiExpr(), self.TV_multi_expr)
        self.translate(self.RepMultiExpr(), self.SV_multi_expr)

    class RepCat(Replicate):
        @comb
        def update(s):
            s.out /= rep(4, cat(s.in2, s.in2))

    TV_rep_cat = [IO(), (None, 0b11, None, None, 0xFFFF)]
    SV_rep_cat = "    __out_bits = {4{in2, in2}};\n"

    def test_rep_cat(self):
        self.simulate(self.RepCat(), self.TV_rep_cat)
        self.translate(self.RepCat(), self.SV_rep_cat)

    class CatRep(Replicate):
        @comb
        def update(s):
            s.out /= cat(rep(2, s.in4), rep(2, s.in4))

    TV_cat_rep = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_cat_rep = "    __out_bits = {{2{in4}}, {2{in4}}};\n"

    def test_cat_rep(self):
        self.simulate(self.CatRep(), self.TV_cat_rep)
        self.translate(self.CatRep(), self.SV_cat_rep)


class TestPowOp(BaseTestCase):
    class PowOp(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in2 = Input(2)
            s.in4 = Input(4)
            s.in8 = Input(8)
            s.out = Output(16)

    class IO(IOStruct):
        in1 = Input()
        in2 = Input(2)
        in4 = Input(4)
        in8 = Input(8)
        out = Output(16)

    class PowVec(PowOp):
        @comb
        def update(s):
            s.out /= s.in8**2

    TV_vec = [IO(), (None, None, None, 0xCD, 0xCDCD)]
    SV_vec = "    __out_bits = {2{in8}};\n"

    def test_vec(self):
        self.simulate(self.PowVec(), self.TV_vec)
        self.translate(self.PowVec(), self.SV_vec)

    class PowBits(PowOp):
        @comb
        def update(s):
            s.out /= b4(0xA) ** 4

    TV_bits = [IO(), (None, None, None, None, 0xAAAA)]
    SV_bits = "    __out_bits = {4{4'hA}};\n"

    def test_bits(self):
        self.simulate(self.PowBits(), self.TV_bits)
        self.translate(self.PowBits(), self.SV_bits)

    class PowExpr(PowOp):
        @comb
        def update(s):
            s.out /= cat((s.in4 & b4(0xF)) ** 3, s.in8[2:6] | 0)

    TV_expr = [IO(), (None, None, 0xA, 0xF0, 0xAAAC)]
    SV_expr = "    __out_bits = {{3{in4 & 4'hF}}, in8[5:2] | 4'h0};\n"

    def test_expr(self):
        self.simulate(self.PowExpr(), self.TV_expr)
        self.translate(self.PowExpr(), self.SV_expr)

    class PowNested(PowOp):
        @comb
        def update(s):
            s.out /= (s.in4**2) ** 2

    TV_nested = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_nested = "    __out_bits = {2{{2{in4}}}};\n"

    def test_nested(self):
        self.simulate(self.PowNested(), self.TV_nested)
        self.translate(self.PowNested(), self.SV_nested)

    class PowCatVec(PowOp):
        @comb
        def update(s):
            s.out /= cat(s.in1, s.in2, s.in1) ** 4

    TV_cat_vec = [IO(), (1, 0b00, None, None, 0x9999)]
    SV_cat_vec = "    __out_bits = {4{in1, in2, in1}};\n"

    def test_cat_vec(self):
        self.simulate(self.PowCatVec(), self.TV_cat_vec)
        self.translate(self.PowCatVec(), self.SV_cat_vec)

    class PawCatBits(PowOp):
        @comb
        def update(s):
            s.out /= cat(b4(0xA), b4(0xB), b4(0xC), b4(0xD)) ** 1

    TV_cat_bits = [IO(), (None, None, None, None, 0xABCD)]
    SV_cat_bits = "    __out_bits = {1{4'hA, 4'hB, 4'hC, 4'hD}};\n"

    def test_cat_bits(self):
        self.simulate(self.PawCatBits(), self.TV_cat_bits)
        self.translate(self.PawCatBits(), self.SV_cat_bits)

    class PawCatExpr(PowOp):
        @comb
        def update(s):
            s.out /= cat(s.in4 & b4(0xF), s.in4 | b4(0x0)) ** 2

    TV_cat_expr = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_cat_expr = "    __out_bits = {2{in4 & 4'hF, in4 | 4'h0}};\n"

    def test_cat_expr(self):
        self.simulate(self.PawCatExpr(), self.TV_cat_expr)
        self.translate(self.PawCatExpr(), self.SV_cat_expr)

    class CatPow(PowOp):
        @comb
        def update(s):
            s.out /= cat(s.in4**2, s.in4**2)

    TV_cat_rep = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_cat_rep = "    __out_bits = {{2{in4}}, {2{in4}}};\n"

    def test_cat_rep(self):
        self.simulate(self.CatPow(), self.TV_cat_rep)
        self.translate(self.CatPow(), self.SV_cat_rep)

    class CountExpr(PowOp):
        @comb
        def update(s):
            s.out /= s.in4 ** ((1 + 2) ^ 7)

    TV_count_expr = [IO(), (None, None, 0xA, None, 0xAAAA)]
    SV_count_expr = "    __out_bits = {4{in4}};\n"

    def test_count_expr(self):
        self.simulate(self.CountExpr(), self.TV_count_expr)
        self.translate(self.CountExpr(), self.SV_count_expr)
