# Tests for HDL expression: unary operations
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


class TestInvert(BaseTestCase):
    class Invert(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in4 = Input(4)
            s.out1 = Output()
            s.out4 = Output(4)

    class IO(IOStruct):
        in1 = Input()
        in4 = Input(4)
        out1 = Output()
        out4 = Output(4)

    class InvertVec(Invert):
        @comb
        def update(s):
            s.out1 /= ~s.in1
            s.out4 /= ~s.in4

    TV_vec = [IO(), (0, 0b1010, 1, 0b0101), (1, 0b0011, 0, 0b1100)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ~in1;\n"
        "    __out4_bits = ~in4;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.InvertVec(), self.TV_vec)
        self.translate(self.InvertVec(), self.SV_vec)

    class InvertBits(Invert):
        @comb
        def update(s):
            s.out1 /= ~b1(0)
            s.out4 /= ~b4(0b0101)

    TV_bits = [IO(), (None, None, 1, 10)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ~(1'h0);\n"
        "    __out4_bits = ~(4'h5);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.InvertBits(), self.TV_bits)
        self.translate(self.InvertBits(), self.SV_bits)

    class InvertBitsLong(Invert):
        @comb
        def update(s):
            s.out1 /= (~b101(0)).P
            s.out4 /= (~TRUE.ext(100)).P.ext(4)

    TV_bits_long = [IO(), (None, None, 1, 1)]
    SV_bits_long = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ^(101'h0 ^ {101{1'h1}});\n"
        "    __out4_bits = {3'h0, ^({99'h0, 1'h1} ^ {100{1'h1}})};\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_long(self):
        self.simulate(self.InvertBitsLong(), self.TV_bits_long)
        self.translate(self.InvertBitsLong(), self.SV_bits_long)

    class InvertInt(Invert):
        @comb
        def update(s):
            s.out1 /= ~0
            s.out4 /= ~5

    TV_int = [IO(), (None, None, 1, 10)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h1;\n"
        "    __out4_bits = 4'hA;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.InvertInt(), self.TV_int)
        self.translate(self.InvertInt(), self.SV_int)

    class InvertIntExpr(Invert):
        @comb
        def update(s):
            s.out1 /= ~(1 & 0)
            s.out4 /= ~((3 + 4) ^ (1 & 7))

    TV_int_expr = [IO(), (None, None, 1, 0b1001)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h1;\n"
        "    __out4_bits = 4'h9;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.InvertIntExpr(), self.TV_int_expr)
        self.translate(self.InvertIntExpr(), self.SV_int_expr)


class TestNot(BaseTestCase):
    class Not(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in4 = Input(4)
            s.out1 = Output()
            s.out4 = Output()  # Boolean output for 4-bit input

    class IO(IOStruct):
        in1 = Input()
        in4 = Input(4)
        out1 = Output()
        out4 = Output()

    class NotVec(Not):
        @comb
        def update(s):
            s.out1 /= not s.in1
            s.out4 /= not s.in4

    TV_vec = [IO(), (0, 0b1010, 1, 0), (1, 0b0011, 0, 0)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ~in1;\n"
        "    __out4_bits = ~(|in4);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.NotVec(), self.TV_vec)
        self.translate(self.NotVec(), self.SV_vec)

    class NotBits(Not):
        @comb
        def update(s):
            s.out1 /= not b1(0)
            s.out4 /= not b4(0b0101)

    TV_bits = [IO(), (None, None, 1, 0)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ~(1'h0);\n"
        "    __out4_bits = ~(|(4'h5));\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.NotBits(), self.TV_bits)
        self.translate(self.NotBits(), self.SV_bits)

    class NotInt(Not):
        @comb
        def update(s):
            s.out1 /= not 0
            s.out4 /= not 5

    TV_int = [IO(), (None, None, 1, 0)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h1;\n"
        "    __out4_bits = 1'h0;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.NotInt(), self.TV_int)
        self.translate(self.NotInt(), self.SV_int)

    class NotIntExpr(Not):
        @comb
        def update(s):
            s.out1 /= not (1 & 0)
            s.out4 /= not ((3 + 4) ^ (1 & 7))

    TV_int_expr = [IO(), (None, None, 1, 0)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h1;\n"
        "    __out4_bits = 1'h0;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.NotIntExpr(), self.TV_int_expr)
        self.translate(self.NotIntExpr(), self.SV_int_expr)

    class NotCompare(Not):
        @comb
        def update(s):
            s.out1 /= not (s.in1 == 0)
            s.out4 /= not (s.in4 == b4(0b1010))

    TV_compare = [IO(), (0, 0b1010, 0, 0), (1, 0b0011, 1, 1)]
    SV_compare = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = ~(in1 == 1'h0);\n"
        "    __out4_bits = ~(in4 == 4'hA);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_compare(self):
        self.simulate(self.NotCompare(), self.TV_compare)
        self.translate(self.NotCompare(), self.SV_compare)


class TestUAdd(BaseTestCase):
    class UAdd(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in4 = Input(4)
            s.out1 = Output()
            s.out4 = Output(4)

    class IO(IOStruct):
        in1 = Input()
        in4 = Input(4)
        out1 = Output()
        out4 = Output(4)

    class UAddVec(UAdd):
        @comb
        def update(s):
            s.out1 /= +s.in1
            s.out4 /= +s.in4

    TV_vec = [IO(), (0, 0b1010, 0, 0b1010), (1, 0b0011, 1, 0b0011)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = in1;\n"
        "    __out4_bits = in4;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.UAddVec(), self.TV_vec)
        self.translate(self.UAddVec(), self.SV_vec)

    class UAddBits(UAdd):
        @comb
        def update(s):
            s.out1 /= +b1(0)
            s.out4 /= +b4(0b0101)

    TV_bits = [IO(), (None, None, 0, 5)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = 4'h5;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.UAddBits(), self.TV_bits)
        self.translate(self.UAddBits(), self.SV_bits)

    class UAddInt(UAdd):
        @comb
        def update(s):
            s.out1 /= +0
            s.out4 /= +5

    TV_int = [IO(), (None, None, 0, 5)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = 4'h5;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.UAddInt(), self.TV_int)
        self.translate(self.UAddInt(), self.SV_int)

    class UAddIntExpr(UAdd):
        @comb
        def update(s):
            s.out1 /= +(1 & 0)
            s.out4 /= +((3 + 4) ^ (1 & 7))

    TV_int_expr = [IO(), (None, None, 0, 6)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = 4'h6;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.UAddIntExpr(), self.TV_int_expr)
        self.translate(self.UAddIntExpr(), self.SV_int_expr)


class TestUSub(BaseTestCase):
    class USub(RawModule):
        @build
        def ports(s):
            s.in1 = Input()
            s.in4 = Input(4)
            s.out1 = Output()
            s.out4 = Output(4)

    class IO(IOStruct):
        in1 = Input()
        in4 = Input(4)
        out1 = Output()
        out4 = Output(4)

    class USubVec(USub):
        @comb
        def update(s):
            s.out1 /= -s.in1
            s.out4 /= -s.in4

    TV_vec = [IO(), (0, 0b1010, 0, 0b0110), (1, 0b0011, 1, 0b1101)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0 - in1;\n"
        "    __out4_bits = 4'h0 - in4;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.USubVec(), self.TV_vec)
        self.translate(self.USubVec(), self.SV_vec)

    class USubBits(USub):
        @comb
        def update(s):
            s.out1 /= -b1(0)
            s.out4 /= -b4(0b0101)

    TV_bits = [IO(), (None, None, 0, 11)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0 - 1'h0;\n"
        "    __out4_bits = 4'h0 - 4'h5;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.USubBits(), self.TV_bits)
        self.translate(self.USubBits(), self.SV_bits)

    class USubInt(USub):
        @comb
        def update(s):
            s.out1 /= -0
            s.out4 /= -5

    TV_int = [IO(), (None, None, 0, 11)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = 4'hB;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.USubInt(), self.TV_int)
        self.translate(self.USubInt(), self.SV_int)

    class USubIntExpr(USub):
        @comb
        def update(s):
            s.out1 /= -(1 & 0)
            s.out4 /= -((3 + 4) ^ (1 & 7))

    TV_int_expr = [IO(), (None, None, 0, 10)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = 4'hA;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.USubIntExpr(), self.TV_int_expr)
        self.translate(self.USubIntExpr(), self.SV_int_expr)
