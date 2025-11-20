# Tests for HDL expression: shift operations
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


class Shift(RawModule):
    @build
    def ports(s):
        s.data = Input(16)
        s.amount = Input(4)
        s.out = Output(16)


class IO(IOStruct):
    data = Input(16)
    amount = Input(4)
    out = Output(16)


# Left shift
#
class TestVecShl(BaseTestCase):
    # vec << min/max
    class VecShlMinMax(Shift):
        @comb
        def update(s):
            s.out /= s.data << 0 | s.data >> 15

    TV_vec_min_max = [IO(), (0xAAAA, None, 0xAAAB), (0xF0F0, None, 0xF0F1)]
    SV_vec_min_max = "    __out_bits = data << 32'h0 | data >> 32'hF;\n"

    def test_vec_min(self):
        self.simulate(self.VecShlMinMax(), self.TV_vec_min_max)
        self.translate(self.VecShlMinMax(), self.SV_vec_min_max)

    # vec << vec
    class VecShlVec(Shift):
        @comb
        def update(s):
            s.out /= s.data << s.amount

    TV_vec_vec = [
        IO(),
        (0xAAAA, 4, 0xAAA0),
        (0xF0F0, 4, 0x0F00),
        (0x1234, 2, 0x48D0),
    ]
    SV_vec_vec = "    __out_bits = data << amount;\n"

    def test_vec_vec(self):
        self.simulate(self.VecShlVec(), self.TV_vec_vec)
        self.translate(self.VecShlVec(), self.SV_vec_vec)

    # vec << vec_expr
    class VecShlVecExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data << (s.amount & 7)

    TV_vec_vec_expr = [
        IO(),
        (0xAAAA, 4, 0xAAA0),
        (0xF0F0, 4, 0x0F00),
        (0x1234, 2, 0x48D0),
    ]
    SV_vec_vec_expr = "    __out_bits = data << (amount & 4'h7);\n"

    def test_vec_vec_expr(self):
        self.simulate(self.VecShlVecExpr(), self.TV_vec_vec_expr)
        self.translate(self.VecShlVecExpr(), self.SV_vec_vec_expr)

    # vec_expr << bits_expr
    class VecExprShlBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (s.data & 0xFFFF) << (b4(2) + b4(1) + 1)

    TV_vec_expr_bits_expr = [
        IO(),
        (0xAAAA, None, 0xAAA0),
        (0xF0F0, None, 0x0F00),
    ]
    SV_vec_expr_bits_expr = (
        "    __out_bits = (data & 16'hFFFF) << 4'h2 + 4'h1 + 4'h1;\n"
    )

    def test_vec_expr_bits_expr(self):
        self.simulate(self.VecExprShlBitsExpr(), self.TV_vec_expr_bits_expr)
        self.translate(self.VecExprShlBitsExpr(), self.SV_vec_expr_bits_expr)

    # vec << int_expr
    class VecShlIntExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data << (4 - 0)

    TV_vec_int_expr = [
        IO(),
        (0xAAAA, None, 0xAAA0),
        (0xF0F0, None, 0x0F00),
    ]
    SV_vec_int_expr = "    __out_bits = data << 32'h4;\n"

    def test_vec_int_expr(self):
        self.simulate(self.VecShlIntExpr(), self.TV_vec_int_expr)
        self.translate(self.VecShlIntExpr(), self.SV_vec_int_expr)


class TestBitsShl(BaseTestCase):
    # bits << bits
    class BitsShlBits(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) << b4(4)

    TV_bits_bits = [
        IO(),
        (None, None, 0xAAA0),
    ]
    SV_bits_bits = "    __out_bits = 16'hAAAA << 4'h4;\n"

    def test_bits_bits(self):
        self.simulate(self.BitsShlBits(), self.TV_bits_bits)
        self.translate(self.BitsShlBits(), self.SV_bits_bits)

    # bits << vec_expr
    class BitsShlVecExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) << (s.amount & 7)

    TV_bits_vec_expr = [
        IO(),
        (None, 4, 0xAAA0),
        (None, 4, 0xAAA0),
        (None, 2, 0xAAA8),
    ]
    SV_bits_vec_expr = "    __out_bits = 16'hAAAA << (amount & 4'h7);\n"

    def test_bits_vec_expr(self):
        self.simulate(self.BitsShlVecExpr(), self.TV_bits_vec_expr)
        self.translate(self.BitsShlVecExpr(), self.SV_bits_vec_expr)

    # bits_expr << bits_expr
    class BitsExprShlBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (b16(0xAAAA) & 0xFFFF) << (b4(2) + b4(1) + 1)

    TV_bits_expr_bits_expr = [
        IO(),
        (None, None, 0xAAA0),
    ]
    SV_bits_expr_bits_expr = (
        "    __out_bits = (16'hAAAA & 16'hFFFF) << 4'h2 + 4'h1 + 4'h1;\n"
    )

    def test_bits_expr_bits_expr(self):
        self.simulate(self.BitsExprShlBitsExpr(), self.TV_bits_expr_bits_expr)
        self.translate(self.BitsExprShlBitsExpr(), self.SV_bits_expr_bits_expr)

    # bits << int_expr
    class BitsShlIntExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) << (4 - 0)

    TV_bits_int_expr = [
        IO(),
        (None, None, 0xAAA0),
    ]
    SV_bits_int_expr = "    __out_bits = 16'hAAAA << 32'h4;\n"

    def test_bits_int_expr(self):
        self.simulate(self.BitsShlIntExpr(), self.TV_bits_int_expr)
        self.translate(self.BitsShlIntExpr(), self.SV_bits_int_expr)


class TestIntShl(BaseTestCase):
    # int << int
    class IntShlInt(Shift):
        @comb
        def update(s):
            s.out /= 0x0AAA << 4

    TV_int_int = [IO(), (None, None, 0xAAA0)]
    SV_int_int = "    __out_bits = 16'hAAA0;\n"

    def test_int_int(self):
        self.simulate(self.IntShlInt(), self.TV_int_int)
        self.translate(self.IntShlInt(), self.SV_int_int)

    # int << int_expr
    class IntShlIntExpr(Shift):
        @comb
        def update(s):
            s.out /= 0x0AAA << (4 - 0)

    TV_int_int_expr = [IO(), (None, None, 0xAAA0)]
    SV_int_int_expr = "    __out_bits = 16'hAAA0;\n"

    def test_int_int_expr(self):
        self.simulate(self.IntShlIntExpr(), self.TV_int_int_expr)
        self.translate(self.IntShlIntExpr(), self.SV_int_int_expr)

    # int_expr << int
    class IntExprShlInt(Shift):
        @comb
        def update(s):
            s.out /= (0xAAAA & 0x0FFF) << 4

    TV_int_expr_int = [IO(), (None, None, 0xAAA0)]
    SV_int_expr_int = "    __out_bits = 16'hAAA0;\n"

    def test_int_expr_int(self):
        self.simulate(self.IntExprShlInt(), self.TV_int_expr_int)
        self.translate(self.IntExprShlInt(), self.SV_int_expr_int)


# Right shift
#
class TestVecShrU(BaseTestCase):
    # vec >> min/max
    class VecShrUMinMax(Shift):
        @comb
        def update(s):
            s.out /= s.data >> 0 | s.data << 15

    TV_vec_min_max = [IO(), (0xAAAA, None, 0xAAAA), (0xF0F0, None, 0xF0F0)]
    SV_vec_min_max = "    __out_bits = data >> 32'h0 | data << 32'hF;\n"

    def test_vec_min(self):
        self.simulate(self.VecShrUMinMax(), self.TV_vec_min_max)
        self.translate(self.VecShrUMinMax(), self.SV_vec_min_max)

    # vec >> vec
    class VecShrUVec(Shift):
        @comb
        def update(s):
            s.out /= s.data >> s.amount

    TV_vec_vec = [
        IO(),
        (0xAAAA, 4, 0x0AAA),
        (0xF0F0, 4, 0x0F0F),
        (0x1234, 2, 0x048D),
    ]
    SV_vec_vec = "    __out_bits = data >> amount;\n"

    def test_vec_vec(self):
        self.simulate(self.VecShrUVec(), self.TV_vec_vec)
        self.translate(self.VecShrUVec(), self.SV_vec_vec)

    # vec >> vec_expr
    class VecShrUVecExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data >> (s.amount & 7)

    TV_vec_vec_expr = [
        IO(),
        (0xAAAA, 4, 0x0AAA),
        (0xF0F0, 4, 0x0F0F),
        (0x1234, 2, 0x048D),
    ]
    SV_vec_vec_expr = "    __out_bits = data >> (amount & 4'h7);\n"

    def test_vec_vec_expr(self):
        self.simulate(self.VecShrUVecExpr(), self.TV_vec_vec_expr)
        self.translate(self.VecShrUVecExpr(), self.SV_vec_vec_expr)

    # vec_expr >> bits_expr
    class VecExprShrUBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (s.data & 0xFFFF) >> (b4(2) + b4(1) + 1)

    TV_vec_expr_bits_expr = [
        IO(),
        (0xAAAA, None, 0x0AAA),
        (0xF0F0, None, 0x0F0F),
    ]
    SV_vec_expr_bits_expr = (
        "    __out_bits = (data & 16'hFFFF) >> 4'h2 + 4'h1 + 4'h1;\n"
    )

    def test_vec_expr_bits_expr(self):
        self.simulate(self.VecExprShrUBitsExpr(), self.TV_vec_expr_bits_expr)
        self.translate(self.VecExprShrUBitsExpr(), self.SV_vec_expr_bits_expr)

    # vec >> int_expr
    class VecShrUIntExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data >> (4 - 0)

    TV_vec_int_expr = [
        IO(),
        (0xAAAA, None, 0x0AAA),
        (0xF0F0, None, 0x0F0F),
    ]
    SV_vec_int_expr = "    __out_bits = data >> 32'h4;\n"

    def test_vec_int_expr(self):
        self.simulate(self.VecShrUIntExpr(), self.TV_vec_int_expr)
        self.translate(self.VecShrUIntExpr(), self.SV_vec_int_expr)


class TestBitsShrU(BaseTestCase):
    # bits >> bits
    class BitsShrUBits(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) >> b4(4)

    TV_bits_bits = [
        IO(),
        (None, None, 0x0AAA),
    ]
    SV_bits_bits = "    __out_bits = 16'hAAAA >> 4'h4;\n"

    def test_bits_bits(self):
        self.simulate(self.BitsShrUBits(), self.TV_bits_bits)
        self.translate(self.BitsShrUBits(), self.SV_bits_bits)

    # bits >> vec_expr
    class BitsShrUVecExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) >> (s.amount & 7)

    TV_bits_vec_expr = [
        IO(),
        (None, 4, 0x0AAA),
        (None, 4, 0x0AAA),
        (None, 2, 0x2AAA),
    ]
    SV_bits_vec_expr = "    __out_bits = 16'hAAAA >> (amount & 4'h7);\n"

    def test_bits_vec_expr(self):
        self.simulate(self.BitsShrUVecExpr(), self.TV_bits_vec_expr)
        self.translate(self.BitsShrUVecExpr(), self.SV_bits_vec_expr)

    # bits_expr >> bits_expr
    class BitsExprShrUBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (b16(0xAAAA) & 0xFFFF) >> (b4(2) + b4(1) + 1)

    TV_bits_expr_bits_expr = [
        IO(),
        (None, None, 0x0AAA),
    ]
    SV_bits_expr_bits_expr = (
        "    __out_bits = (16'hAAAA & 16'hFFFF) >> 4'h2 + 4'h1 + 4'h1;\n"
    )

    def test_bits_expr_bits_expr(self):
        self.simulate(self.BitsExprShrUBitsExpr(), self.TV_bits_expr_bits_expr)
        self.translate(
            self.BitsExprShrUBitsExpr(), self.SV_bits_expr_bits_expr
        )

    # bits >> int_expr
    class BitsShrUIntExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA) >> (4 - 0)

    TV_bits_int_expr = [
        IO(),
        (None, None, 0x0AAA),
    ]
    SV_bits_int_expr = "    __out_bits = 16'hAAAA >> 32'h4;\n"

    def test_bits_int_expr(self):
        self.simulate(self.BitsShrUIntExpr(), self.TV_bits_int_expr)
        self.translate(self.BitsShrUIntExpr(), self.SV_bits_int_expr)


class TestIntShrU(BaseTestCase):
    # int >> int
    class IntShrUInt(Shift):
        @comb
        def update(s):
            s.out /= 0xAAAA >> 4

    TV_int_int = [IO(), (None, None, 0x0AAA)]
    SV_int_int = "    __out_bits = 16'hAAA;\n"

    def test_int_int(self):
        self.simulate(self.IntShrUInt(), self.TV_int_int)
        self.translate(self.IntShrUInt(), self.SV_int_int)

    # int >> int_expr
    class IntShrUIntExpr(Shift):
        @comb
        def update(s):
            s.out /= 0xAAAA >> (4 - 0)

    TV_int_int_expr = [IO(), (None, None, 0x0AAA)]
    SV_int_int_expr = "    __out_bits = 16'hAAA;\n"

    def test_int_int_expr(self):
        self.simulate(self.IntShrUIntExpr(), self.TV_int_int_expr)
        self.translate(self.IntShrUIntExpr(), self.SV_int_int_expr)

    # int_expr >> int
    class IntExprShrUInt(Shift):
        @comb
        def update(s):
            s.out /= (0xAAAA & 0xFFFF) >> 4

    TV_int_expr_int = [IO(), (None, None, 0x0AAA)]
    SV_int_expr_int = "    __out_bits = 16'hAAA;\n"

    def test_int_expr_int(self):
        self.simulate(self.IntExprShrUInt(), self.TV_int_expr_int)
        self.translate(self.IntExprShrUInt(), self.SV_int_expr_int)


# Arithmetic right shift
#
class TestVecShrS(BaseTestCase):
    # vec.S >> min/max
    class VecShrSMinMax(Shift):
        @comb
        def update(s):
            s.out /= s.data.S >> 0 | s.data.S >> 15

    TV_vec_min_max = [
        IO(),
        (0xAAAA, None, (0xAAAA | 0xFFFF)),
        (0xF0F0, None, (0xF0F0 | 0xFFFF)),
    ]
    SV_vec_min_max = (
        "    __out_bits = $signed($signed(data) >>> 32'h0) "
        "| $signed($signed(data) >>> 32'hF);\n"
    )

    def test_vec_min_max(self):
        self.simulate(self.VecShrSMinMax(), self.TV_vec_min_max)
        self.translate(self.VecShrSMinMax(), self.SV_vec_min_max)

    # vec.S >> vec
    class VecShrSVec(Shift):
        @comb
        def update(s):
            s.out /= s.data.S >> s.amount

    TV_vec_vec = [
        IO(),
        (0xAAAA, 4, 0xFAAA),
        (0xF0F0, 4, 0xFF0F),
        (0x1234, 2, 0x048D),
    ]
    SV_vec_vec = "    __out_bits = $signed($signed(data) >>> amount);\n"

    def test_vec_vec(self):
        self.simulate(self.VecShrSVec(), self.TV_vec_vec)
        self.translate(self.VecShrSVec(), self.SV_vec_vec)

    # vec.S >> vec_expr
    class VecShrSVecExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data.S >> (s.amount & 7)

    TV_vec_vec_expr = [
        IO(),
        (0xAAAA, 4, 0xFAAA),
        (0xF0F0, 4, 0xFF0F),
        (0x1234, 2, 0x048D),
    ]
    SV_vec_vec_expr = (
        "    __out_bits = $signed($signed(data) >>> (amount & 4'h7));\n"
    )

    def test_vec_vec_expr(self):
        self.simulate(self.VecShrSVecExpr(), self.TV_vec_vec_expr)
        self.translate(self.VecShrSVecExpr(), self.SV_vec_vec_expr)

    # vec_expr.S >> bits_expr
    class VecExprShrSBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (s.data & 0xFFFF).S >> (b4(2) + b4(1) + 1)

    TV_vec_expr_bits_expr = [
        IO(),
        (0xAAAA, None, 0xFAAA),
        (0xF0F0, None, 0xFF0F),
    ]
    SV_vec_expr_bits_expr = (
        "    __out_bits = $signed($signed(data & 16'hFFFF) "
        ">>> 4'h2 + 4'h1 + 4'h1);\n"
    )

    def test_vec_expr_bits_expr(self):
        self.simulate(self.VecExprShrSBitsExpr(), self.TV_vec_expr_bits_expr)
        self.translate(self.VecExprShrSBitsExpr(), self.SV_vec_expr_bits_expr)

    # vec.S >> int_expr
    class VecShrSIntExpr(Shift):
        @comb
        def update(s):
            s.out /= s.data.S >> (4 - 0)

    TV_vec_int_expr = [
        IO(),
        (0xAAAA, None, 0xFAAA),
        (0xF0F0, None, 0xFF0F),
    ]
    SV_vec_int_expr = "    __out_bits = $signed($signed(data) >>> 32'h4);\n"

    def test_vec_int_expr(self):
        self.simulate(self.VecShrSIntExpr(), self.TV_vec_int_expr)
        self.translate(self.VecShrSIntExpr(), self.SV_vec_int_expr)


class TestBitsShrS(BaseTestCase):
    # bits.S >> bits
    class BitsShrSBits(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA).S >> b4(4)

    TV_bits_bits = [
        IO(),
        (None, None, 0xFAAA),
    ]
    SV_bits_bits = "    __out_bits = $signed(-16'sh5556 >>> 4'h4);\n"

    def test_bits_bits(self):
        self.simulate(self.BitsShrSBits(), self.TV_bits_bits)
        self.translate(self.BitsShrSBits(), self.SV_bits_bits)

    # bits.S >> vec_expr
    class BitsShrSVecExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA).S >> (s.amount & 7)

    TV_bits_vec_expr = [
        IO(),
        (None, 4, 0xFAAA),
        (None, 4, 0xFAAA),
        (None, 2, 0xEAAA),
    ]
    SV_bits_vec_expr = (
        "    __out_bits = $signed(-16'sh5556 >>> (amount & 4'h7));\n"
    )

    def test_bits_vec_expr(self):
        self.simulate(self.BitsShrSVecExpr(), self.TV_bits_vec_expr)
        self.translate(self.BitsShrSVecExpr(), self.SV_bits_vec_expr)

    # bits_expr.S >> bits_expr
    class BitsExprShrSBitsExpr(Shift):
        @comb
        def update(s):
            s.out /= (b16(0xAAAA) & 0xFFFF).S >> (b4(2) + b4(1) + 1)

    TV_bits_expr_bits_expr = [
        IO(),
        (None, None, 0xFAAA),
    ]
    SV_bits_expr_bits_expr = (
        "    __out_bits = $signed($signed(16'hAAAA & 16'hFFFF) "
        ">>> 4'h2 + 4'h1 + 4'h1);\n"
    )

    def test_bits_expr_bits_expr(self):
        self.simulate(self.BitsExprShrSBitsExpr(), self.TV_bits_expr_bits_expr)
        self.translate(
            self.BitsExprShrSBitsExpr(), self.SV_bits_expr_bits_expr
        )

    # bits.S >> int_expr
    class BitsShrSIntExpr(Shift):
        @comb
        def update(s):
            s.out /= b16(0xAAAA).S >> (4 - 0)

    TV_bits_int_expr = [
        IO(),
        (None, None, 0xFAAA),
    ]
    SV_bits_int_expr = "    __out_bits = $signed(-16'sh5556 >>> 32'h4);\n"

    def test_bits_int_expr(self):
        self.simulate(self.BitsShrSIntExpr(), self.TV_bits_int_expr)
        self.translate(self.BitsShrSIntExpr(), self.SV_bits_int_expr)
