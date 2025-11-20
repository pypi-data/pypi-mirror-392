# Tests for HDL expression: bitwise operations
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


# Bitwise INVERT is tested in expr_unary_test.


class TestBitAnd(BaseTestCase):
    class BitAnd(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit & 1-bit
            s.out44 = Output(4)  # 4-bit & 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecAndVec(BitAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a & s.in1b
            s.out44 /= s.in4a & s.in4b

    TV_vec_vec = [
        IO(),
        (0, 1, 0b1010, 0b0011, 0, 0b0010),
        (1, 1, 0b1111, 0b1010, 1, 0b1010),
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a & in1b;\n"
        "    __out44_bits = in4a & in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecAndVec(), self.TV_vec_vec)
        self.translate(self.VecAndVec(), self.SV_vec_vec)

    class VecAndBits(BitAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a & b1(1)
            s.out44 /= b4(0b1100) & s.in4a

    TV_vec_bits = [
        IO(),
        (0, None, 0b1010, None, 0, 0b1000),
        (1, None, 0b1111, None, 1, 0b1100),
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a & 1'h1;\n"
        "    __out44_bits = 4'hC & in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecAndBits(), self.TV_vec_bits)
        self.translate(self.VecAndBits(), self.SV_vec_bits)

    class VecAndInt(BitAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a & 1
            s.out44 /= 0b0101 & s.in4a

    TV_vec_int = [
        IO(),
        (None, None, 0b1010, None, 0, 0b0000),
        (1, None, 0b1111, None, 1, 0b0101),
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a & 1'h1;\n"
        "    __out44_bits = 4'h5 & in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecAndInt(), self.TV_vec_int)
        self.translate(self.VecAndInt(), self.SV_vec_int)

    class BitsAndBits(BitAnd):
        @comb
        def update(s):
            s.out11 /= b1(0) & b1(1)
            s.out44 /= b4(0b1010) & b4(0b0011)

    TV_bits_bits = [IO(), (None, None, None, None, 0, 0b0010)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 & 1'h1;\n"
        "    __out44_bits = 4'hA & 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsAndBits(), self.TV_bits_bits)
        self.translate(self.BitsAndBits(), self.SV_bits_bits)

    class BitsAndInt(BitAnd):
        @comb
        def update(s):
            s.out11 /= b1(1) & 0
            s.out44 /= 0b1100 & b4(0b1010)

    TV_bits_int = [IO(), (None, None, None, None, 0, 0b1000)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 & 1'h0;\n"
        "    __out44_bits = 4'hC & 4'hA;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsAndInt(), self.TV_bits_int)
        self.translate(self.BitsAndInt(), self.SV_bits_int)

    class IntAndInt(BitAnd):
        @comb
        def update(s):
            s.out11 /= 1 & 0
            s.out44 /= 0b1010 & 0b0011

    TV_int_int = [IO(), (None, None, None, None, 0, 0b0010)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0;\n"
        "    __out44_bits = 4'h2;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntAndInt(), self.TV_int_int)
        self.translate(self.IntAndInt(), self.SV_int_int)

    class IntExprAndVec(BitAnd):
        @comb
        def update(s):
            s.out11 /= (~(1 & 0)) & s.in1a
            s.out44 /= (0b0101 & 0b1100) & s.in4a

    TV_int_expr_vec = [IO(), (1, None, 0b0011, None, 1, 0b0000)]
    SV_int_expr_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 & in1a;\n"
        "    __out44_bits = 4'h4 & in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr_vec(self):
        self.simulate(self.IntExprAndVec(), self.TV_int_expr_vec)
        self.translate(self.IntExprAndVec(), self.SV_int_expr_vec)


class TestBitOr(BaseTestCase):
    class BitOr(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit | 1-bit
            s.out44 = Output(4)  # 4-bit | 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecOrVec(BitOr):
        @comb
        def update(s):
            s.out11 /= s.in1a | s.in1b
            s.out44 /= s.in4a | s.in4b

    TV_vec_vec = [
        IO(),
        (0, 0, 0b1010, 0b0011, 0, 0b1011),
        (1, 0, 0b1111, 0b1010, 1, 0b1111),
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a | in1b;\n"
        "    __out44_bits = in4a | in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecOrVec(), self.TV_vec_vec)
        self.translate(self.VecOrVec(), self.SV_vec_vec)

    class VecOrBits(BitOr):
        @comb
        def update(s):
            s.out11 /= s.in1a | b1(0)
            s.out44 /= b4(0b1100) | s.in4a

    TV_vec_bits = [
        IO(),
        (0, None, 0b1010, None, 0, 0b1110),
        (1, None, 0b1111, None, 1, 0b1111),
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a | 1'h0;\n"
        "    __out44_bits = 4'hC | in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecOrBits(), self.TV_vec_bits)
        self.translate(self.VecOrBits(), self.SV_vec_bits)

    class VecOrInt(BitOr):
        @comb
        def update(s):
            s.out11 /= s.in1a | 0
            s.out44 /= 0b0101 | s.in4a

    TV_vec_int = [
        IO(),
        (0, None, 0b1010, None, 0, 0b1111),
        (1, None, 0b1111, None, 1, 0b1111),
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a | 1'h0;\n"
        "    __out44_bits = 4'h5 | in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecOrInt(), self.TV_vec_int)
        self.translate(self.VecOrInt(), self.SV_vec_int)

    class BitsOrBits(BitOr):
        @comb
        def update(s):
            s.out11 /= b1(0) | b1(1)
            s.out44 /= b4(0b1010) | b4(0b0011)

    TV_bits_bits = [IO(), (None, None, None, None, 1, 0b1011)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 | 1'h1;\n"
        "    __out44_bits = 4'hA | 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsOrBits(), self.TV_bits_bits)
        self.translate(self.BitsOrBits(), self.SV_bits_bits)

    class BitsOrInt(BitOr):
        @comb
        def update(s):
            s.out11 /= b1(0) | 1
            s.out44 /= 0b0101 | b4(0b1010)

    TV_bits_int = [IO(), (None, None, None, None, 1, 0b1111)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 | 1'h1;\n"
        "    __out44_bits = 4'h5 | 4'hA;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsOrInt(), self.TV_bits_int)
        self.translate(self.BitsOrInt(), self.SV_bits_int)

    class IntOrInt(BitOr):
        @comb
        def update(s):
            s.out11 /= 1 | 0
            s.out44 /= 0b1010 | 0b0011

    TV_int_int = [IO(), (None, None, None, None, 1, 0b1011)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 4'hB;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntOrInt(), self.TV_int_int)
        self.translate(self.IntOrInt(), self.SV_int_int)

    class IntExprOrVec(BitOr):
        @comb
        def update(s):
            s.out11 /= (not (3 & 0)) | s.in1a
            s.out44 /= (0b0101 | 0b1100) | s.in4a

    TV_int_expr_vec = [IO(), (0, None, 0b0010, None, 1, 0b1111)]
    SV_int_expr_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 | in1a;\n"
        "    __out44_bits = 4'hD | in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr_vec(self):
        self.simulate(self.IntExprOrVec(), self.TV_int_expr_vec)
        self.translate(self.IntExprOrVec(), self.SV_int_expr_vec)


class TestBitXor(BaseTestCase):
    class BitXor(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit ^ 1-bit
            s.out44 = Output(4)  # 4-bit ^ 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecXorVec(BitXor):
        @comb
        def update(s):
            s.out11 /= s.in1a ^ s.in1b
            s.out44 /= s.in4a ^ s.in4b

    TV_vec_vec = [
        IO(),
        (0, 0, 0b1010, 0b0011, 0, 0b1001),
        (1, 0, 0b1111, 0b1010, 1, 0b0101),
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a ^ in1b;\n"
        "    __out44_bits = in4a ^ in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecXorVec(), self.TV_vec_vec)
        self.translate(self.VecXorVec(), self.SV_vec_vec)

    class VecXorBits(BitXor):
        @comb
        def update(s):
            s.out11 /= s.in1a ^ b1(1)
            s.out44 /= b4(0b1100) ^ s.in4a

    TV_vec_bits = [
        IO(),
        (0, None, 0b1010, None, 1, 0b0110),
        (1, None, 0b1111, None, 0, 0b0011),
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = ~in1a;\n"
        "    __out44_bits = 4'hC ^ in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecXorBits(), self.TV_vec_bits)
        self.translate(self.VecXorBits(), self.SV_vec_bits)

    class VecXorInt(BitXor):
        @comb
        def update(s):
            s.out11 /= s.in1a ^ 1
            s.out44 /= 0b0101 ^ s.in4a

    TV_vec_int = [
        IO(),
        (0, None, 0b1010, None, 1, 0b1111),
        (1, None, 0b1111, None, 0, 0b1010),
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = ~in1a;\n"
        "    __out44_bits = 4'h5 ^ in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecXorInt(), self.TV_vec_int)
        self.translate(self.VecXorInt(), self.SV_vec_int)

    class BitsXorBits(BitXor):
        @comb
        def update(s):
            s.out11 /= b1(0) ^ b1(1)
            s.out44 /= b4(0b1010) ^ b4(0b0011)

    TV_bits_bits = [IO(), (None, None, None, None, 1, 0b1001)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = ~(1'h0);\n"
        "    __out44_bits = 4'hA ^ 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsXorBits(), self.TV_bits_bits)
        self.translate(self.BitsXorBits(), self.SV_bits_bits)

    class BitsXorInt(BitXor):
        @comb
        def update(s):
            s.out11 /= b1(0) ^ 1
            s.out44 /= 0b1100 ^ b4(0b1010)

    TV_bits_int = [IO(), (None, None, None, None, 1, 0b0110)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = ~(1'h0);\n"
        "    __out44_bits = 4'hC ^ 4'hA;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsXorInt(), self.TV_bits_int)
        self.translate(self.BitsXorInt(), self.SV_bits_int)

    class IntXorInt(BitXor):
        @comb
        def update(s):
            s.out11 /= 1 ^ 0
            s.out44 /= 0b1010 ^ 0b0011

    TV_int_int = [IO(), (None, None, None, None, 1, 0b1001)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 4'h9;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntXorInt(), self.TV_int_int)
        self.translate(self.IntXorInt(), self.SV_int_int)

    class IntExprXorVec(BitXor):
        @comb
        def update(s):
            s.out11 /= (-(1 | 0)) ^ s.in1a
            s.out44 /= (0b0101 ^ 0b1100) ^ s.in4a

    TV_int_expr_vec = [IO(), (0, None, 0b0010, None, 1, 0b1011)]
    SV_int_expr_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 ^ in1a;\n"
        "    __out44_bits = 4'h9 ^ in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr_vec(self):
        self.simulate(self.IntExprXorVec(), self.TV_int_expr_vec)
        self.translate(self.IntExprXorVec(), self.SV_int_expr_vec)
