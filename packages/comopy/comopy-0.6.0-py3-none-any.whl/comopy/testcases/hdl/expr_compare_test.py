# Tests for HDL expression: comparisons
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


class Compare(RawModule):
    @build
    def build_all(s):
        s.a = Input(8)
        s.b = Input(8)
        s.out = Output()


class IO(IOStruct):
    a = Input(8)
    b = Input(8)
    out = Output()


class TestVecCompare(BaseTestCase):
    # vec == vec
    class VecEqVec(Compare):
        @comb
        def update(s):
            s.out /= s.a == s.b

    TV_vec_eq_vec = [IO(), (0x12, 0x34, 0), (0x56, 0x56, 1)]
    SV_vec_eq_vec = "    __out_bits = a == b;"

    def test_vec_eq_vec(self):
        self.simulate(self.VecEqVec(), self.TV_vec_eq_vec)
        self.translate(self.VecEqVec(), self.SV_vec_eq_vec)

    # bool != vec
    class BoolNeVec(Compare):
        @build
        def assign(s):
            s.out @= Bool(s.a and s.b) != s.a[0]

    TV_bool_ne_vec = [IO(), (0x12, 0x34, 1), (0x55, 0x77, 0)]
    SV_bool_ne_vec = "  assign __out_bits = ((|a) & (|b)) != a[0];"

    def test_bool_ne_vec(self):
        self.simulate(self.BoolNeVec(), self.TV_bool_ne_vec)
        self.translate(self.BoolNeVec(), self.SV_bool_ne_vec)

    # vec != bool
    class VecNeBool(Compare):
        @comb
        def update(s):
            s.out /= s.a[0] != Bool(s.a or s.b)

    TV_vec_ne_bool = [IO(), (0x12, 0x34, 1), (0x55, 0x77, 0)]
    SV_vec_ne_bool = "    __out_bits = a[0] != ((|a) | (|b));"

    def test_vec_ne_bool(self):
        self.simulate(self.VecNeBool(), self.TV_bool_ne_vec)
        self.translate(self.VecNeBool(), self.SV_vec_ne_bool)

    # vec > not
    class VecGtNot(Compare):
        @comb
        def update(s):
            s.out /= s.a[0] > (not s.b[0])

    TV_vec_gt_not = [IO(), (0x12, 0x34, 0), (0x55, 0x77, 1)]
    SV_vec_gt_not = "    __out_bits = a[0] > ~(b[0]);"

    def test_vec_gt_not(self):
        self.simulate(self.VecGtNot(), self.TV_vec_gt_not)
        self.translate(self.VecGtNot(), self.SV_vec_gt_not)

    # vec_expr < vec_expr
    class VecLtVec(Compare):
        @comb
        def update(s):
            s.out /= (s.a & s.b) < (s.a | s.b)

    TV_vec_lt_vec = [IO(), (0x12, 0x34, 1), (0x56, 0x56, 0)]
    SV_vec_lt_vec = "    __out_bits = (a & b) < (a | b);"

    def test_vec_lt_vec(self):
        self.simulate(self.VecLtVec(), self.TV_vec_lt_vec)
        self.translate(self.VecLtVec(), self.SV_vec_lt_vec)

    # vec <= bits
    class VecLeBits(Compare):
        @comb
        def update(s):
            s.out /= s.a <= b8(0x0F) & b8(0xFF)

    TV_vec_le_bits = [IO(), (0x12, None, 0), (0x0F, None, 1)]
    SV_vec_le_bits = "    __out_bits = a <= (8'hF & 8'hFF);"

    def test_le_vec_bits(self):
        self.simulate(self.VecLeBits(), self.TV_vec_le_bits)
        self.translate(self.VecLeBits(), self.SV_vec_le_bits)

    # bits >= vec
    class BitsGeVec(Compare):
        @comb
        def update(s):
            s.out /= b8(0x0F) + b8(0) >= s.b

    TV_bits_ge_vec = [IO(), (None, 0x12, 0), (None, 0x0F, 1)]
    SV_bits_ge_vec = "    __out_bits = 8'hF + 8'h0 >= b;"

    def test_bits_ge_vec(self):
        self.simulate(self.BitsGeVec(), self.TV_bits_ge_vec)
        self.translate(self.BitsGeVec(), self.SV_bits_ge_vec)

    # vec <= int
    class VecLeInt(Compare):
        @comb
        def update(s):
            s.out /= s.a <= 0x0F

    TV_vec_le_int = [IO(), (0x12, None, 0), (0x0F, None, 1)]
    SV_vec_le_int = "    __out_bits = a <= 8'hF;"

    def test_le_vec_int(self):
        self.simulate(self.VecLeInt(), self.TV_vec_le_int)
        self.translate(self.VecLeInt(), self.SV_vec_le_int)

    # int >= vec
    class IntGeVec(Compare):
        @comb
        def update(s):
            s.out /= 0x0F >= s.b

    TV_int_ge_vec = [IO(), (None, 0x12, 0), (None, 0x0F, 1)]
    SV_int_ge_vec = "    __out_bits = 8'hF >= b;"

    def test_int_ge_vec(self):
        self.simulate(self.IntGeVec(), self.TV_int_ge_vec)
        self.translate(self.IntGeVec(), self.SV_int_ge_vec)

    # vec != int_expr
    class VecNeIntExpr(Compare):
        @comb
        def update(s):
            s.out /= s.a != (0x10 + 0x02)

    TV_vec_ne_int_expr = [IO(), (0x12, None, 0), (0x11, None, 1)]
    SV_vec_ne_int_expr = "    __out_bits = a != 8'h12;"

    def test_ne_vec_int_expr(self):
        self.simulate(self.VecNeIntExpr(), self.TV_vec_ne_int_expr)
        self.translate(self.VecNeIntExpr(), self.SV_vec_ne_int_expr)


class TestBitsCompare(BaseTestCase):
    # bits == bits
    class BitsEqBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x12) == b8(0x34)

    TV_bits_eq_bits = [IO(), (None, None, 0)]
    SV_bits_eq_bits = "    __out_bits = 8'h12 == 8'h34;"

    def test_bits_eq_bits(self):
        self.simulate(self.BitsEqBits(), self.TV_bits_eq_bits)
        self.translate(self.BitsEqBits(), self.SV_bits_eq_bits)

    # bits != bits
    class BitsNeBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x12) != b8(0x12)

    TV_bits_ne_bits = [IO(), (None, None, 0)]
    SV_bits_ne_bits = "    __out_bits = 8'h12 != 8'h12;"

    def test_bits_ne_bits(self):
        self.simulate(self.BitsNeBits(), self.TV_bits_ne_bits)
        self.translate(self.BitsNeBits(), self.SV_bits_ne_bits)

    # bits < bits
    class BitsLtBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x12) < b8(0x34)

    TV_bits_lt_bits = [IO(), (None, None, 1)]
    SV_bits_lt_bits = "    __out_bits = 8'h12 < 8'h34;"

    def test_bits_lt_bits(self):
        self.simulate(self.BitsLtBits(), self.TV_bits_lt_bits)
        self.translate(self.BitsLtBits(), self.SV_bits_lt_bits)

    # bits <= bits
    class BitsLeBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x34) <= b8(0x34)

    TV_bits_le_bits = [IO(), (None, None, 1)]
    SV_bits_le_bits = "    __out_bits = 8'h34 <= 8'h34;"

    def test_bits_le_bits(self):
        self.simulate(self.BitsLeBits(), self.TV_bits_le_bits)
        self.translate(self.BitsLeBits(), self.SV_bits_le_bits)

    # bits > bits
    class BitsGtBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x56) > b8(0x12)

    TV_bits_gt_bits = [IO(), (None, None, 1)]
    SV_bits_gt_bits = "    __out_bits = 8'h56 > 8'h12;"

    def test_bits_gt_bits(self):
        self.simulate(self.BitsGtBits(), self.TV_bits_gt_bits)
        self.translate(self.BitsGtBits(), self.SV_bits_gt_bits)

    # bits >= bits
    class BitsGeBits(Compare):
        @comb
        def update(s):
            s.out /= b8(0x78) >= b8(0x56)

    TV_bits_ge_bits = [IO(), (None, None, 1)]
    SV_bits_ge_bits = "    __out_bits = 8'h78 >= 8'h56;"

    def test_bits_ge_bits(self):
        self.simulate(self.BitsGeBits(), self.TV_bits_ge_bits)
        self.translate(self.BitsGeBits(), self.SV_bits_ge_bits)

    # bits expr == bits expr
    class BitsExprEqBitsExpr(Compare):
        @comb
        def update(s):
            s.out /= (b8(0x0F) & b8(0xFF)) == (b8(0xF0) >> 4)

    TV_bits_expr_eq = [IO(), (None, None, 1)]
    SV_bits_expr_eq = "    __out_bits = (8'hF & 8'hFF) == 8'hF0 >> 32'h4;"

    def test_bits_expr_eq_bits_expr(self):
        self.simulate(self.BitsExprEqBitsExpr(), self.TV_bits_expr_eq)
        self.translate(self.BitsExprEqBitsExpr(), self.SV_bits_expr_eq)

    # bits expr != int expr
    class BitsExprNeIntExpr(Compare):
        @comb
        def update(s):
            s.out /= (b8(0x0F) & b8(0xFF)) != (0x10 - 0x01)

    TV_bits_expr_ne_int = [IO(), (None, None, 0)]
    SV_bits_expr_ne_int = "    __out_bits = (8'hF & 8'hFF) != 8'hF;"

    def test_bits_expr_ne_int_expr(self):
        self.simulate(self.BitsExprNeIntExpr(), self.TV_bits_expr_ne_int)
        self.translate(self.BitsExprNeIntExpr(), self.SV_bits_expr_ne_int)


class TestIntCompare(BaseTestCase):
    # int == int (constant folding)
    class IntEqInt(Compare):
        @comb
        def update(s):
            s.out /= 0x12 == 0x34

    TV_int_eq_int = [IO(), (None, None, 0)]
    SV_int_eq_int = "    __out_bits = 1'h0;"

    def test_int_eq_int(self):
        self.simulate(self.IntEqInt(), self.TV_int_eq_int)
        self.translate(self.IntEqInt(), self.SV_int_eq_int)

    # int != int (constant folding)
    class IntNeInt(Compare):
        @comb
        def update(s):
            s.out /= 0x12 != 0x12

    TV_int_ne_int = [IO(), (None, None, 0)]
    SV_int_ne_int = "    __out_bits = 1'h0;"

    def test_int_ne_int(self):
        self.simulate(self.IntNeInt(), self.TV_int_ne_int)
        self.translate(self.IntNeInt(), self.SV_int_ne_int)

    # int < int (constant folding)
    class IntLtInt(Compare):
        @comb
        def update(s):
            s.out /= 0x12 < 0x34

    TV_int_lt_int = [IO(), (None, None, 1)]
    SV_int_lt_int = "    __out_bits = 1'h1;"

    def test_int_lt_int(self):
        self.simulate(self.IntLtInt(), self.TV_int_lt_int)
        self.translate(self.IntLtInt(), self.SV_int_lt_int)

    # int <= int (constant folding)
    class IntLeInt(Compare):
        @comb
        def update(s):
            s.out /= 0x34 <= 0x34

    TV_int_le_int = [IO(), (None, None, 1)]
    SV_int_le_int = "    __out_bits = 1'h1;"

    def test_int_le_int(self):
        self.simulate(self.IntLeInt(), self.TV_int_le_int)
        self.translate(self.IntLeInt(), self.SV_int_le_int)

    # int > int (constant folding)
    class IntGtInt(Compare):
        @comb
        def update(s):
            s.out /= 0x56 > 0x12

    TV_int_gt_int = [IO(), (None, None, 1)]
    SV_int_gt_int = "    __out_bits = 1'h1;"

    def test_int_gt_int(self):
        self.simulate(self.IntGtInt(), self.TV_int_gt_int)
        self.translate(self.IntGtInt(), self.SV_int_gt_int)

    # int >= int (constant folding)
    class IntGeInt(Compare):
        @comb
        def update(s):
            s.out /= 0x78 >= 0x56

    TV_int_ge_int = [IO(), (None, None, 1)]
    SV_int_ge_int = "    __out_bits = 1'h1;"

    def test_int_ge_int(self):
        self.simulate(self.IntGeInt(), self.TV_int_ge_int)
        self.translate(self.IntGeInt(), self.SV_int_ge_int)

    # int expr == int expr (constant folding)
    class IntExprEqIntExpr(Compare):
        @comb
        def update(s):
            s.out /= (0x10 + 0x02) == (0x20 - 0x0E)

    TV_int_expr_eq_int_expr = [IO(), (None, None, 1)]
    SV_int_expr_eq_int_expr = "    __out_bits = 1'h1;"

    def test_int_expr_eq_int_expr(self):
        self.simulate(self.IntExprEqIntExpr(), self.TV_int_expr_eq_int_expr)
        self.translate(self.IntExprEqIntExpr(), self.SV_int_expr_eq_int_expr)


class TestVecCompareS(BaseTestCase):
    # vec.S == vec.S
    class VecEqsVec(Compare):
        @comb
        def update(s):
            s.out /= s.a.S == s.b.S

    TV_vec_eqs_vec = [IO(), (0x12, 0x34, 0), (0x80, 0x80, 1)]
    SV_vec_eqs_vec = "    __out_bits = a == b;\n"

    def test_vec_eqs_vec(self):
        self.simulate(self.VecEqsVec(), self.TV_vec_eqs_vec)
        self.translate(self.VecEqsVec(), self.SV_vec_eqs_vec)

    # vec.S == int
    class VecEqsInt(Compare):
        @comb
        def update(s):
            s.out /= s.a.S == -128

    TV_vec_eqs_int = [IO(), (0x12, None, 0), (0x80, None, 1)]
    SV_vec_eqs_int = "    __out_bits = a == 8'h80;\n"

    # int != vec.S
    class IntNesVec(Compare):
        @comb
        def update(s):
            s.out /= -128 != s.a.S

    TV_int_nes_vec = [IO(), (0x12, None, 1), (0x80, None, 0)]
    SV_int_nes_vec = "    __out_bits = 8'h80 != a;\n"

    def test_vec_nes_int(self):
        self.simulate(self.IntNesVec(), self.TV_int_nes_vec)
        self.translate(self.IntNesVec(), self.SV_int_nes_vec)

    # vec.S > vec.S
    class VecGtsVec(Compare):
        @comb
        def update(s):
            s.out /= s.a.S > s.b.S

    TV_vec_gts_vec = [
        IO(),
        (0x12, 0x34, 0),
        (0x90, 0xA0, 0),
        (0xFE, 0x7F, 0),
        (0x7F, 0x80, 1),
        (0x00, 0x80, 1),
        (0x00, 0x7F, 0),
    ]
    SV_vec_gts_vec = "    __out_bits = $signed(a) > $signed(b);\n"

    def test_vec_gts_vec(self):
        self.simulate(self.VecGtsVec(), self.TV_vec_gts_vec)
        self.translate(self.VecGtsVec(), self.SV_vec_gts_vec)

    # vec_expr.S < vec_expr.S
    class VecLtsVec(Compare):
        @comb
        def update(s):
            s.out /= (s.a & s.b).S < (s.a | s.b).S

    TV_vec_lts_vec = [
        IO(),
        (0x12, 0x34, 1),  # (0x12 & 0x34) < (0x12 | 0x34) => 0x10 < 0x36
        (0x90, 0xA0, 1),  # (0x90 & 0xA0) < (0x90 | 0xA0) => 0x80 < 0xB0
        (0xFE, 0x7F, 0),  # (0xFE & 0x7F) < (0xFE | 0x7F) => 0x7E < 0xFF
        (0x7F, 0x80, 0),  # (0x7F & 0x80) < (0x7F | 0x80) => 0x00 < 0xFF
        (0x00, 0x80, 0),  # (0x00 & 0x80) < (0x00 | 0x80) => 0x00 < 0x80
        (0x00, 0x7F, 1),  # (0x00 & 0x7F) < (0x00 | 0x7F) => 0x00 < 0x7F
    ]
    SV_vec_lts_vec = "    __out_bits = $signed(a & b) < $signed(a | b);\n"

    def test_vec_lts_vec(self):
        self.simulate(self.VecLtsVec(), self.TV_vec_lts_vec)
        self.translate(self.VecLtsVec(), self.SV_vec_lts_vec)

    # Bits.S >= vec.S
    class BitsGesVec(Compare):
        @comb
        def update(s):
            s.out /= b8(-2).S >= s.b.S

    TV_bits_ges_vec = [
        IO(),
        (None, 0x7F, 0),  # -2 >= 127
        (None, 0x80, 1),  # -2 >= -128
        (None, 0xFD, 1),  # -2 >= -3
        (None, 0xFE, 1),  # -2 >= -2
        (None, 0xFF, 0),  # -2 >= -1
    ]
    SV_bits_ges_vec = "    __out_bits = -8'sh2 >= $signed(b);\n"

    def test_bits_ges_vec(self):
        self.simulate(self.BitsGesVec(), self.TV_bits_ges_vec)
        self.translate(self.BitsGesVec(), self.SV_bits_ges_vec)

    # vec.S <= Bits.S
    class VecLesBits(Compare):
        @comb
        def update(s):
            s.out /= s.a.S <= b8(-2).S

    TV_vec_les_bits = [
        IO(),
        (0x7F, None, 0),  # 127 <= -2
        (0x80, None, 1),  # -128 <= -2
        (0xFD, None, 1),  # -3 <= -2
        (0xFE, None, 1),  # -2 <= -2
        (0xFF, None, 0),  # -1 <= -2
    ]
    SV_vec_les_bits = "    __out_bits = $signed(a) <= -8'sh2;\n"

    def test_vec_les_bits(self):
        self.simulate(self.VecLesBits(), self.TV_vec_les_bits)
        self.translate(self.VecLesBits(), self.SV_vec_les_bits)

    # int > vec_expr.S
    class IntGtsVec(Compare):
        @comb
        def update(s):
            s.out /= -2 > (s.a | s.b).S

    TV_int_gts_vec = [
        IO(),
        (0x00, 0x7F, 0),  # -2 > signed(0x00 | 0x7F) => -2 > 127
        (0x80, 0x81, 1),  # -2 > signed(0x80 | 0x81) => -2 > -127
        (0xFC, 0xFD, 1),  # -2 > signed(0xFC | 0xFD) => -2 > -3
        (0xFE, 0xFF, 0),  # -2 > signed(0xFE | 0xFF) => -2 > -1
    ]
    SV_int_gts_vec = "    __out_bits = -8'sh2 > $signed(a | b);\n"

    def test_int_gts_vec(self):
        self.simulate(self.IntGtsVec(), self.TV_int_gts_vec)
        self.translate(self.IntGtsVec(), self.SV_int_gts_vec)

    # vec_expr.S < int
    class VecLtsInt(Compare):
        @comb
        def update(s):
            s.out /= (s.a | s.b).S < -2

    TV_vec_lts_int = [
        IO(),
        (0x00, 0x7F, 0),  # signed(0x00 | 0x7F) < -2 => 127 < -2
        (0x80, 0x81, 1),  # signed(0x80 | 0x81) < -2 => -127 < -2
        (0xFC, 0xFD, 1),  # signed(0xFC | 0xFD) < -2 => -3 < -2
        (0xFE, 0xFF, 0),  # signed(0xFE | 0xFF) < -2 => -1 < -2
    ]
    SV_vec_lts_int = "    __out_bits = $signed(a | b) < -8'sh2;\n"

    def test_vec_lts_int(self):
        self.simulate(self.VecLtsInt(), self.TV_vec_lts_int)
        self.translate(self.VecLtsInt(), self.SV_vec_lts_int)


class TestBitsCompareS(BaseTestCase):
    # Bits.S == Bits.S
    class BitsEqsBits(Compare):
        @comb
        def update(s):
            s.out /= b8(-12).S == b8(-34).S

    TV_bits_eqs_bits = [IO(), (None, None, 0)]
    SV_bits_eqs_bits = "    __out_bits = 8'hF4 == 8'hDE;\n"

    def test_bits_eqs_bits(self):
        self.simulate(self.BitsEqsBits(), self.TV_bits_eqs_bits)
        self.translate(self.BitsEqsBits(), self.SV_bits_eqs_bits)

    # Bits.S == int
    class BitsEqsInt(Compare):
        @comb
        def update(s):
            s.out /= b8(-12).S == -12

    TV_bits_eqs_int = [IO(), (None, None, 1)]
    SV_bits_eqs_int = "    __out_bits = 8'hF4 == 8'hF4;\n"

    def test_bits_eqs_int(self):
        self.simulate(self.BitsEqsInt(), self.TV_bits_eqs_int)
        self.translate(self.BitsEqsInt(), self.SV_bits_eqs_int)

    # int != Bits.S
    class IntNesBits(Compare):
        @comb
        def update(s):
            s.out /= -12 != b8(-12).S

    TV_int_nes_bits = [IO(), (None, None, 0)]
    SV_int_nes_bits = "    __out_bits = 8'hF4 != 8'hF4;\n"

    def test_int_nes_bits(self):
        self.simulate(self.IntNesBits(), self.TV_int_nes_bits)
        self.translate(self.IntNesBits(), self.SV_int_nes_bits)

    # Bits.S > Bits.S
    class BitsGtsBits(Compare):
        @comb
        def update(s):
            s.out /= b8(-5).S > b8(-10).S

    TV_bits_gts_bits = [IO(), (None, None, 1)]
    SV_bits_gts_bits = "    __out_bits = -8'sh5 > -8'shA;\n"

    def test_bits_gts_bits(self):
        self.simulate(self.BitsGtsBits(), self.TV_bits_gts_bits)
        self.translate(self.BitsGtsBits(), self.SV_bits_gts_bits)

    # Bits.S < Bits.S
    class BitsLtsBits(Compare):
        @comb
        def update(s):
            s.out /= b8(-10).S < b8(-5).S

    TV_bits_lts_bits = [IO(), (None, None, 1)]
    SV_bits_lts_bits = "    __out_bits = -8'shA < -8'sh5;\n"

    def test_bits_lts_bits(self):
        self.simulate(self.BitsLtsBits(), self.TV_bits_lts_bits)
        self.translate(self.BitsLtsBits(), self.SV_bits_lts_bits)

    # Bits.S >= int
    class BitsGesInt(Compare):
        @comb
        def update(s):
            s.out /= b8(-5).S >= -5  # -5 >= -5

    TV_bits_ges_int = [IO(), (None, None, 1)]
    SV_bits_ges_int = "    __out_bits = -8'sh5 >= -8'sh5;\n"

    def test_bits_ges_int(self):
        self.simulate(self.BitsGesInt(), self.TV_bits_ges_int)
        self.translate(self.BitsGesInt(), self.SV_bits_ges_int)

    # int <= Bits.S
    class IntLesBits(Compare):
        @comb
        def update(s):
            s.out /= -10 <= b8(-10).S  # -10 <= -10

    TV_int_les_bits = [IO(), (None, None, 1)]
    SV_int_les_bits = "    __out_bits = -8'shA <= -8'shA;\n"

    def test_int_les_bits(self):
        self.simulate(self.IntLesBits(), self.TV_int_les_bits)
        self.translate(self.IntLesBits(), self.SV_int_les_bits)
