# Tests for HDL expression: conditional operation
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


class TestCondOp(BaseTestCase):
    class CondOp(RawModule):
        @build
        def ports(s):
            s.sel = Input(3)
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)

    class IO(IOStruct):
        sel = Input(3)
        in1 = Input(8)
        in2 = Input(8)
        out = Output(8)

    class BoolVecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if s.sel == 1 else s.in2

    TV_bool_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xCD),
        (1, 0xAB, 0xCD, 0xAB),
        (2, 0x12, 0x34, 0x34),
    ]
    SV_bool_vec_vec = "    __out_bits = sel == 3'h1 ? in1 : in2;\n"

    def test_bool_vec_vec(self):
        self.simulate(self.BoolVecVec(), self.TV_bool_vec_vec)
        self.translate(self.BoolVecVec(), self.SV_bool_vec_vec)

    class BoolVecBits(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 & 0xF0 if s.sel > 2 else b8(0xA5)

    TV_bool_vec_bits = [
        IO(),
        (0, 0xAB, 0xCD, 0xA5),
        (2, 0xAB, 0xCD, 0xA5),
        (3, 0x12, 0x34, 0x10),
        (5, 0x78, 0x9A, 0x70),
    ]
    SV_bool_vec_bits = "    __out_bits = sel > 3'h2 ? in1 & 8'hF0 : 8'hA5;\n"

    def test_vec_expr_bits(self):
        self.simulate(self.BoolVecBits(), self.TV_bool_vec_bits)
        self.translate(self.BoolVecBits(), self.SV_bool_vec_bits)

    class BoolIntVec(CondOp):
        @comb
        def update(s):
            s.out /= 42 if s.sel & 1 else s.in2

    TV_bool_int_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xCD),
        (1, 0xAB, 0xCD, 42),
        (2, 0x12, 0x34, 0x34),
        (3, 0x56, 0x78, 42),
    ]
    SV_bool_int_vec = "    __out_bits = (|(sel & 3'h1)) ? 8'h2A : in2;\n"

    def test_bool_int_vec(self):
        self.simulate(self.BoolIntVec(), self.TV_bool_int_vec)
        self.translate(self.BoolIntVec(), self.SV_bool_int_vec)

    class BoolBitsBits(CondOp):
        @comb
        def update(s):
            s.out /= (b8(0xFF) | b8(0xAB)) if Bool(s.sel) else b8(5) - 5

    TV_bool_bits_bits = [
        IO(),
        (0, 0xAB, 0xCD, 0x00),
        (1, 0xAB, 0xCD, 0xFF),
        (3, 0x12, 0x34, 0xFF),
        (7, 0x56, 0x78, 0xFF),
    ]
    SV_bool_bits_bits = (
        "    __out_bits = (|sel) ? 8'hFF | 8'hAB : 8'h5 - 8'h5;\n"
    )

    def test_bool_bits_bits(self):
        self.simulate(self.BoolBitsBits(), self.TV_bool_bits_bits)
        self.translate(self.BoolBitsBits(), self.SV_bool_bits_bits)

    class BoolBitsInt(CondOp):
        @comb
        def update(s):
            s.out /= b8(0xCC) if s.sel >= 4 and s.sel <= 6 else (2 << 2) + 2

    TV_bool_bits_int = [
        IO(),
        (0, 0xAB, 0xCD, 0x0A),
        (3, 0xAB, 0xCD, 0x0A),
        (4, 0x12, 0x34, 0xCC),
        (5, 0x56, 0x78, 0xCC),
        (6, 0x9A, 0xBC, 0xCC),
        (7, 0xDE, 0xF0, 0x0A),
    ]
    SV_bool_bits_int = (
        "    __out_bits = sel >= 3'h4 & sel <= 3'h6 ? 8'hCC : 8'hA;\n"
    )

    def test_bool_bits_int(self):
        self.simulate(self.BoolBitsInt(), self.TV_bool_bits_int)
        self.translate(self.BoolBitsInt(), self.SV_bool_bits_int)

    class ScalarVecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if s.sel[0] else s.in2

    TV_scalar_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xCD),
        (1, 0xAB, 0xCD, 0xAB),
        (2, 0x12, 0x34, 0x34),
        (3, 0x56, 0x78, 0x56),
    ]
    SV_scalar_vec_vec = "    __out_bits = sel[0] ? in1 : in2;\n"

    def test_scalar_vec_vec(self):
        self.simulate(self.ScalarVecVec(), self.TV_scalar_vec_vec)
        self.translate(self.ScalarVecVec(), self.SV_scalar_vec_vec)

    class VecVecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if s.sel else s.in2

    TV_vec_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xCD),
        (1, 0xAB, 0xCD, 0xAB),
        (2, 0x12, 0x34, 0x12),
        (3, 0x56, 0x78, 0x56),
    ]
    SV_vec_vec_vec = "    __out_bits = (|sel) ? in1 : in2;\n"

    def test_vec_vec_vec(self):
        self.simulate(self.VecVecVec(), self.TV_vec_vec_vec)
        self.translate(self.VecVecVec(), self.SV_vec_vec_vec)

    class Bits1VecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if TRUE else s.in2

    TV_b1_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xAB),
        (1, 0x12, 0x34, 0x12),
        (7, 0x56, 0x78, 0x56),
    ]
    SV_b1_vec_vec = "    __out_bits = 1'h1 ? in1 : in2;\n"

    def test_b1_vec_vec(self):
        self.simulate(self.Bits1VecVec(), self.TV_b1_vec_vec)
        self.translate(self.Bits1VecVec(), self.SV_b1_vec_vec)

    class BitsVecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if b8(8) else s.in2

    TV_bits_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xAB),
        (1, 0x12, 0x34, 0x12),
        (7, 0x56, 0x78, 0x56),
    ]
    SV_bits_vec_vec = "    __out_bits = (|(8'h8)) ? in1 : in2;\n"

    def test_bits_vec_vec(self):
        self.simulate(self.BitsVecVec(), self.TV_bits_vec_vec)
        self.translate(self.BitsVecVec(), self.SV_bits_vec_vec)

    class IntVecVec(CondOp):
        @comb
        def update(s):
            s.out /= s.in1 if 8 else s.in2

    TV_int_vec_vec = [
        IO(),
        (0, 0xAB, 0xCD, 0xAB),  # 8 is always true
        (1, 0x12, 0x34, 0x12),  # 8 is always true
        (7, 0x56, 0x78, 0x56),  # 8 is always true
    ]
    SV_int_vec_vec = "    __out_bits = 1'h1 ? in1 : in2;\n"

    def test_int_vec_vec(self):
        self.simulate(self.IntVecVec(), self.TV_int_vec_vec)
        self.translate(self.IntVecVec(), self.SV_int_vec_vec)

    class IntIntInt(CondOp):
        @comb
        def update(s):
            s.out /= 200 + 55 if 8 else 16 << 3

    TV_init_int_int = [
        IO(),
        (0, 0xAB, 0xCD, 255),
        (1, 0xAB, 0xCD, 255),
        (3, 0x12, 0x34, 255),
        (7, 0x56, 0x78, 255),
    ]
    SV_int_int_int = "    __out_bits = 8'hFF;\n"

    def test_bool_int_int(self):
        self.simulate(self.IntIntInt(), self.TV_init_int_int)
        self.translate(self.IntIntInt(), self.SV_int_int_int)


class TestNestedCondOp(BaseTestCase):
    class NestedCondOp(RawModule):
        @build
        def ports(s):
            s.sel1 = Input()
            s.sel2 = Input(3)
            s.flag = Input()
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.in3 = Input(8)
            s.out = Output(8)

    class IO(IOStruct):
        sel1 = Input()
        sel2 = Input(3)
        flag = Input()
        in1 = Input(8)
        in2 = Input(8)
        in3 = Input(8)
        out = Output(8)

    class IfElseIf(NestedCondOp):
        @comb
        def update(s):
            s.out /= s.in1 if s.sel1 else (s.in2 if s.flag else s.in3)

    TV_if_else_if = [
        IO(),
        (0, 0, 0, 0xAA, 0xBB, 0xCC, 0xCC),  # sel1=0, flag=0
        (0, 0, 1, 0xAA, 0xBB, 0xCC, 0xBB),  # sel1=0, flag=1
        (1, 0, 0, 0xAA, 0xBB, 0xCC, 0xAA),  # sel1=1
        (1, 0, 1, 0xAA, 0xBB, 0xCC, 0xAA),  # sel1=1
    ]
    SV_if_else_if = "    __out_bits = sel1 ? in1 : flag ? in2 : in3;\n"

    def test_if_else_if(self):
        self.simulate(self.IfElseIf(), self.TV_if_else_if)
        self.translate(self.IfElseIf(), self.SV_if_else_if)

    class IfIfElseElse(NestedCondOp):
        @comb
        def update(s):
            s.out /= (
                (b8(0x55) if s.sel2 > 2 else s.in1)
                if s.sel1 & s.flag
                else (s.in2 ^ 0xAA)
            )

    TV_if_if_else_else = [
        IO(),
        (0, 0, 0, 0x11, 0x22, 0x33, 0x88),  # sel1&flag=0
        (0, 1, 1, 0x11, 0x22, 0x33, 0x88),  # sel1&flag=0
        (1, 0, 1, 0x11, 0x22, 0x33, 0x11),  # sel1&flag=1, sel2<=2
        (1, 3, 1, 0x11, 0x22, 0x33, 0x55),  # sel1&flag=1, sel2>2
        (1, 7, 1, 0x44, 0x55, 0x66, 0x55),  # sel1&flag=1, sel2>2
    ]
    SV_if_if_else_else = (
        "    __out_bits = sel1 & flag ? (sel2 > 3'h2 ? 8'h55 : in1)"
        " : in2 ^ 8'hAA;\n"
    )

    def test_if_if_else_else(self):
        self.simulate(self.IfIfElseElse(), self.TV_if_if_else_else)
        self.translate(self.IfIfElseElse(), self.SV_if_if_else_else)

    class DeepNested(NestedCondOp):
        @comb
        def update(s):
            s.out /= (
                42
                if s.sel1
                else (
                    b8(0xFF) + b8(1)
                    if s.sel2 == 1
                    else (s.in1 << 1 if s.flag else 128 - 8)
                )
            )

    TV_deep_nested = [
        IO(),
        (0, 0, 0, 0x10, 0x20, 0x30, 120),  # sel1=0, sel2!=1, flag=0
        (0, 0, 1, 0x10, 0x20, 0x30, 0x20),  # sel1=0, sel2!=1, flag=1
        (0, 1, 0, 0x10, 0x20, 0x30, 0x00),  # sel1=0, sel2==1
        (0, 1, 1, 0x10, 0x20, 0x30, 0x00),  # sel1=0, sel2==1
        (1, 0, 0, 0x10, 0x20, 0x30, 42),  # sel1=1
        (1, 7, 1, 0x40, 0x50, 0x60, 42),  # sel1=1
    ]
    SV_deep_nested = (
        "    __out_bits = sel1 ? 8'h2A : sel2 == 3'h1 ? 8'hFF + 8'h1"
        " : flag ? in1 << 32'h1 : 8'h78;\n"
    )

    def test_deep_nested(self):
        self.simulate(self.DeepNested(), self.TV_deep_nested)
        self.translate(self.DeepNested(), self.SV_deep_nested)

    class MixedExprs(NestedCondOp):
        @comb
        def update(s):
            s.out /= (
                (b8(0x33) | b8(0x44))
                if s.sel2[0]
                else (
                    (16 + 8) << 1
                    if s.sel2[1]
                    else (s.in1 & s.in2 if s.sel2[2] else b8(0xAB) - b8(0x11))
                )
            )

    TV_mixed_exprs = [
        IO(),
        (0, 0, 0, 0xF0, 0x0F, 0x99, 0x9A),  # sel2=0b000, sel2[2]=0
        (0, 1, 0, 0xF0, 0x0F, 0x99, 0x77),  # sel2=0b001, sel2[0]=1
        (0, 2, 0, 0xF0, 0x0F, 0x99, 48),  # sel2=0b010, sel2[1]=1
        (0, 3, 0, 0xF0, 0x0F, 0x99, 0x77),  # sel2=0b011, sel2[0]=1
        (0, 4, 0, 0xF0, 0x0F, 0x99, 0x00),  # sel2=0b100, sel2[2]=1
        (0, 5, 0, 0xF0, 0x0F, 0x99, 0x77),  # sel2=0b101, sel2[0]=1
    ]
    SV_mixed_exprs = (
        "    __out_bits =\n"
        "      sel2[0] ? 8'h33 | 8'h44 : sel2[1] ? 8'h30 : sel2[2] ? in1 & in2"
        " : 8'hAB - 8'h11;\n"
    )

    def test_mixed_exprs(self):
        self.simulate(self.MixedExprs(), self.TV_mixed_exprs)
        self.translate(self.MixedExprs(), self.SV_mixed_exprs)

    class AsymmetricNesting(NestedCondOp):
        @comb
        def update(s):
            s.out /= (
                s.in1
                if s.sel1
                else (
                    s.in2
                    if s.sel2 & 1
                    else (
                        s.in3
                        if s.sel2 > 4
                        else (b8(0x99) if s.flag else 7 << 2)
                    )
                )
            )

    TV_asymmetric_nesting = [
        IO(),
        (0, 0, 0, 0x11, 0x22, 0x33, 28),  # sel1=0, sel2&1=0, sel2<=4, flag=0
        (0, 0, 1, 0x11, 0x22, 0x33, 0x99),  # sel1=0, sel2&1=0, sel2<=4, flag=1
        (0, 1, 0, 0x11, 0x22, 0x33, 0x22),  # sel1=0, sel2&1=1
        (0, 3, 1, 0x11, 0x22, 0x33, 0x22),  # sel1=0, sel2&1=1
        (0, 6, 0, 0x11, 0x22, 0x33, 0x33),  # sel1=0, sel2&1=0, sel2>4
        (1, 0, 0, 0x44, 0x55, 0x66, 0x44),  # sel1=1
    ]
    SV_asymmetric_nesting = (
        "    __out_bits =\n"
        "      sel1 ? in1 : (|(sel2 & 3'h1)) ? in2 : sel2 > 3'h4 ? in3"
        " : flag ? 8'h99 : 8'h1C;\n"
    )

    def test_asymmetric_nesting(self):
        self.simulate(self.AsymmetricNesting(), self.TV_asymmetric_nesting)
        self.translate(self.AsymmetricNesting(), self.SV_asymmetric_nesting)
