# Tests for HDL expression: arithmetic operations
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


# Arithmetic UAdd/USub are tested in expr_unary_test.


class TestAdd(BaseTestCase):
    class Add(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit + 1-bit
            s.out44 = Output(4)  # 4-bit + 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecAddVec(Add):
        @comb
        def update(s):
            s.out11 /= s.in1a + s.in1b
            s.out44 /= s.in4a + s.in4b

    TV_vec_vec = [
        IO(),
        (0, 1, 0b0101, 0b0011, 1, 0b1000),
        (1, 1, 0b1111, 0b0001, 0, 0b0000),  # overflow: 1+1=0, 15+1=0
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a + in1b;\n"
        "    __out44_bits = in4a + in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecAddVec(), self.TV_vec_vec)
        self.translate(self.VecAddVec(), self.SV_vec_vec)

    class VecAddBits(Add):
        @comb
        def update(s):
            s.out11 /= s.in1a + b1(1)
            s.out44 /= b4(0b0100) + s.in4a

    TV_vec_bits = [
        IO(),
        (0, None, 0b1010, None, 1, 0b1110),
        (1, None, 0b1100, None, 0, 0b0000),  # overflow
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a - 1'h1;\n"
        "    __out44_bits = 4'h4 + in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecAddBits(), self.TV_vec_bits)
        self.translate(self.VecAddBits(), self.SV_vec_bits)

    class VecAddInt(Add):
        @comb
        def update(s):
            s.out11 /= s.in1a + 1
            s.out44 /= 0b0101 + s.in4a

    TV_vec_int = [
        IO(),
        (0, None, 0b1010, None, 1, 0b1111),
        (1, None, 0b1011, None, 0, 0b0000),  # overflow
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a - 1'h1;\n"
        "    __out44_bits = 4'h5 + in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecAddInt(), self.TV_vec_int)
        self.translate(self.VecAddInt(), self.SV_vec_int)

    class BitsAddBits(Add):
        @comb
        def update(s):
            s.out11 /= b1(0) + b1(1)
            s.out44 /= b4(0b1010) + b4(0b0011)

    TV_bits_bits = [IO(), (None, None, None, None, 1, 0b1101)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 - 1'h1;\n"
        "    __out44_bits = 4'hA + 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsAddBits(), self.TV_bits_bits)
        self.translate(self.BitsAddBits(), self.SV_bits_bits)

    class BitsAddInt(Add):
        @comb
        def update(s):
            s.out11 /= b1(1) + 0
            s.out44 /= 3 + b4(0b1000)

    TV_bits_int = [IO(), (None, None, None, None, 1, 0b1011)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 + 1'h0;\n"
        "    __out44_bits = 4'h3 - 4'h8;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsAddInt(), self.TV_bits_int)
        self.translate(self.BitsAddInt(), self.SV_bits_int)

    class IntAddInt(Add):
        @comb
        def update(s):
            s.out11 /= 1 + 0
            s.out44 /= 5 + 3

    TV_int_int = [IO(), (None, None, None, None, 1, 0b1000)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 4'h8;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntAddInt(), self.TV_int_int)
        self.translate(self.IntAddInt(), self.SV_int_int)

    class IntExprAddVec(Add):
        @comb
        def update(s):
            s.out11 /= (+(1 | 0)) + s.in1a
            s.out44 /= (5 + 3) + s.in4a

    TV_vec_int_expr = [IO(), (0, None, 0b0010, None, 1, 0b1010)]
    SV_vec_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 + in1a;\n"
        "    __out44_bits = 4'h8 + in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int_expr(self):
        self.simulate(self.IntExprAddVec(), self.TV_vec_int_expr)
        self.translate(self.IntExprAddVec(), self.SV_vec_int_expr)


class TestSub(BaseTestCase):
    class Sub(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit - 1-bit
            s.out44 = Output(4)  # 4-bit - 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecSubVec(Sub):
        @comb
        def update(s):
            s.out11 /= s.in1a - s.in1b
            s.out44 /= s.in4a - s.in4b

    TV_vec_vec = [
        IO(),
        (1, 0, 0b1000, 0b0011, 1, 0b0101),
        (0, 1, 0b0001, 0b0010, 1, 0b1111),  # underflow: 0-1=1, 1-2=15
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a - in1b;\n"
        "    __out44_bits = in4a - in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecSubVec(), self.TV_vec_vec)
        self.translate(self.VecSubVec(), self.SV_vec_vec)

    class VecSubBits(Sub):
        @comb
        def update(s):
            s.out11 /= s.in1a - b1(0)
            s.out44 /= b4(0b1010) - s.in4a

    TV_vec_bits = [
        IO(),
        (1, None, 0b0011, None, 1, 0b0111),
        (0, None, 0b1100, None, 0, 0b1110),  # 10-12=14
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a - 1'h0;\n"
        "    __out44_bits = 4'hA - in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecSubBits(), self.TV_vec_bits)
        self.translate(self.VecSubBits(), self.SV_vec_bits)

    class VecSubInt(Sub):
        @comb
        def update(s):
            s.out11 /= s.in1a - 1
            s.out44 /= 0b1100 - s.in4a

    TV_vec_int = [
        IO(),
        (1, None, 0b0101, None, 0, 0b0111),
        (0, None, 0b1110, None, 1, 0b1110),  # 12-14=14 (underflow)
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a - 1'h1;\n"
        "    __out44_bits = 4'hC - in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecSubInt(), self.TV_vec_int)
        self.translate(self.VecSubInt(), self.SV_vec_int)

    class BitsSubBits(Sub):
        @comb
        def update(s):
            s.out11 /= b1(1) - b1(0)
            s.out44 /= b4(0b1010) - b4(0b0011)

    TV_bits_bits = [IO(), (None, None, None, None, 1, 0b0111)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 - 1'h0;\n"
        "    __out44_bits = 4'hA - 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsSubBits(), self.TV_bits_bits)
        self.translate(self.BitsSubBits(), self.SV_bits_bits)

    class BitsSubInt(Sub):
        @comb
        def update(s):
            s.out11 /= b1(1) - 0
            s.out44 /= 0b1000 - b4(0b0011)

    TV_bits_int = [IO(), (None, None, None, None, 1, 0b0101)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 - 1'h0;\n"
        "    __out44_bits = 4'h8 - 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsSubInt(), self.TV_bits_int)
        self.translate(self.BitsSubInt(), self.SV_bits_int)

    class IntSubInt(Sub):
        @comb
        def update(s):
            s.out11 /= 1 - 0
            s.out44 /= 8 - 3

    TV_int_int = [IO(), (None, None, None, None, 1, 0b0101)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 4'h5;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntSubInt(), self.TV_int_int)
        self.translate(self.IntSubInt(), self.SV_int_int)

    class IntExprSubVec(Sub):
        @comb
        def update(s):
            s.out11 /= -(1 ^ (not 5)) - s.in1a
            s.out44 /= (8 - 3) - s.in4a

    TV_vec_int_expr = [IO(), (0, None, 0b0010, None, 1, 0b0011)]
    SV_vec_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 - in1a;\n"
        "    __out44_bits = 4'h5 - in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int_expr(self):
        self.simulate(self.IntExprSubVec(), self.TV_vec_int_expr)
        self.translate(self.IntExprSubVec(), self.SV_vec_int_expr)


class TestMul(BaseTestCase):
    class Mul(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit * 1-bit
            s.out44 = Output(4)  # 4-bit * 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output(4)

    class VecMulVec(Mul):
        @comb
        def update(s):
            s.out11 /= s.in1a * s.in1b
            s.out44 /= s.in4a * s.in4b

    TV_vec_vec = [
        IO(),
        (0, 0, 3, 2, 0, 6),
        (0, 1, 4, 4, 0, 0),
        (1, 0, 7, 3, 0, 5),
        (1, 1, 5, 5, 1, 9),
    ]
    SV_vec_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a * in1b;\n"
        "    __out44_bits = in4a * in4b;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_vec(self):
        self.simulate(self.VecMulVec(), self.TV_vec_vec)
        self.translate(self.VecMulVec(), self.SV_vec_vec)

    class VecMulBits(Mul):
        @comb
        def update(s):
            s.out11 /= s.in1a * b1(1)
            s.out44 /= b4(3) * s.in4a

    TV_vec_bits = [
        IO(),
        (0, None, 3, None, 0, 9),
        (1, None, 4, None, 1, 12),
        (1, None, 5, None, 1, 15),
        (1, None, 7, None, 1, 5),  # overflow: 21 -> 5
    ]
    SV_vec_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a * 1'h1;\n"
        "    __out44_bits = 4'h3 * in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_bits(self):
        self.simulate(self.VecMulBits(), self.TV_vec_bits)
        self.translate(self.VecMulBits(), self.SV_vec_bits)

    class VecMulInt(Mul):
        @comb
        def update(s):
            s.out11 /= s.in1a * 1
            s.out44 /= 2 * s.in4a

    TV_vec_int = [
        IO(),
        (0, None, 3, None, 0, 6),
        (1, None, 4, None, 1, 8),
        (1, None, 7, None, 1, 14),
        (1, None, 8, None, 1, 0),  # overflow: 16 -> 0
    ]
    SV_vec_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a * 1'h1;\n"
        "    __out44_bits = 4'h2 * in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int(self):
        self.simulate(self.VecMulInt(), self.TV_vec_int)
        self.translate(self.VecMulInt(), self.SV_vec_int)

    class BitsMulBits(Mul):
        @comb
        def update(s):
            s.out11 /= b1(1) * b1(0)
            s.out44 /= b4(5) * b4(3)

    TV_bits_bits = [IO(), (None, None, None, None, 0, 15)]
    SV_bits_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 * 1'h0;\n"
        "    __out44_bits = 4'h5 * 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_bits(self):
        self.simulate(self.BitsMulBits(), self.TV_bits_bits)
        self.translate(self.BitsMulBits(), self.SV_bits_bits)

    class BitsMulInt(Mul):
        @comb
        def update(s):
            s.out11 /= b1(1) * 0
            s.out44 /= 4 * b4(3)

    TV_bits_int = [IO(), (None, None, None, None, 0, 12)]
    SV_bits_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 * 1'h0;\n"
        "    __out44_bits = 4'h4 * 4'h3;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits_int(self):
        self.simulate(self.BitsMulInt(), self.TV_bits_int)
        self.translate(self.BitsMulInt(), self.SV_bits_int)

    class IntMulInt(Mul):
        @comb
        def update(s):
            s.out11 /= 1 * 0
            s.out44 /= 3 * 4

    TV_int_int = [IO(), (None, None, None, None, 0, 12)]
    SV_int_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0;\n"
        "    __out44_bits = 4'hC;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_int(self):
        self.simulate(self.IntMulInt(), self.TV_int_int)
        self.translate(self.IntMulInt(), self.SV_int_int)

    class IntExprMulVec(Mul):
        @comb
        def update(s):
            s.out11 /= (+(1 & 1)) * s.in1a
            s.out44 /= (2 * 3) * s.in4a

    TV_vec_int_expr = [IO(), (0, None, 2, None, 0, 12)]
    SV_vec_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1 * in1a;\n"
        "    __out44_bits = 4'h6 * in4a;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec_int_expr(self):
        self.simulate(self.IntExprMulVec(), self.TV_vec_int_expr)
        self.translate(self.IntExprMulVec(), self.SV_vec_int_expr)
