# Tests for HDL expression: boolean operations
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


class TestBoolBit(BaseTestCase):
    class BoolBit(RawModule):
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

    class BoolVec(BoolBit):
        @comb
        def update(s):
            s.out1 /= s.in1
            s.out4 /= Bool(s.in4)

    TV_vec = [IO(), (0, 0b1010, 0, 1), (1, 0b0000, 1, 0)]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = in1;\n"
        "    __out4_bits = |in4;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.BoolVec(), self.TV_vec)
        self.translate(self.BoolVec(), self.SV_vec)

    class BoolBits(BoolBit):
        @comb
        def update(s):
            s.out1 /= b1(0)
            s.out4 /= Bool(b4(0b0101))

    TV_bits = [IO(), (None, None, 0, 1)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = |(4'h5);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.BoolBits(), self.TV_bits)
        self.translate(self.BoolBits(), self.SV_bits)

    class BoolInt(BoolBit):
        @comb
        def update(s):
            s.out1 /= Bool(0)
            s.out4 /= s.in4[Bool(5)]  # int folding

    TV_int = [IO(), (None, 0b1010, 0, 1)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out4_bits = in4[1'h1 +: 1];\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.BoolInt(), self.TV_int)
        self.translate(self.BoolInt(), self.SV_int)

    class BoolIntExpr(BoolBit):
        @comb
        def update(s):
            s.out1 /= Bool(~(1 & 0))
            s.out4 /= s.in4[Bool(3 & (5 - 3))]  # int folding

    TV_int_expr = [IO(), (None, 0b1010, 1, 1)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h1;\n"
        "    __out4_bits = in4[1'h1 +: 1];\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.BoolIntExpr(), self.TV_int_expr)
        self.translate(self.BoolIntExpr(), self.SV_int_expr)


# Boolean expressions allowed without an explicit Bool()
class TestNoBoolBit(BaseTestCase):
    class NoBoolBit(RawModule):
        @build
        def ports(s):
            s.a = Input(4)
            s.b = Input(4)
            s.out = Output()

    class IO(IOStruct):
        a = Input(4)
        b = Input(4)
        out = Output()

    class NotVecExpr(NoBoolBit):
        @build
        def connect(s):
            s.out @= not (s.a & s.b)

    TV_not_vec_expr = [IO(), (0b1010, 0b1001, 0), (0b1100, 0b0011, 1)]
    SV_not_vec_expr = "  assign __out_bits = ~(|(a & b));\n"

    def test_not_vec_expr(self):
        self.simulate(self.NotVecExpr(), self.TV_not_vec_expr)
        self.translate(self.NotVecExpr(), self.SV_not_vec_expr)

    class NotBoolExpr(NoBoolBit):
        @build
        def connect(s):
            s.out @= not (s.a and s.b)

    TV_not_bool_expr = [IO(), (0b1010, 0b1001, 0), (0b1100, 0, 1)]
    SV_not_bool_expr = "  assign __out_bits = ~((|a) & (|b));\n"

    def test_not_bool_expr(self):
        self.simulate(self.NotBoolExpr(), self.TV_not_bool_expr)
        self.translate(self.NotBoolExpr(), self.SV_not_bool_expr)

    class BoolNot(NoBoolBit):
        @build
        def connect(s):
            # No Bool() for inner NOT
            s.out @= Bool(s.a and not s.b)

    TV_bool_not = [IO(), (10, 5, 0), (3, 0, 1)]
    SV_bool_not = "  assign __out_bits = (|a) & ~(|b);\n"

    def test_bool_not(self):
        self.simulate(self.BoolNot(), self.TV_bool_not)
        self.translate(self.BoolNot(), self.SV_bool_not)

    class BoolAndOr(NoBoolBit):
        @build
        def connect(s):
            # No Bool() for inner OR
            s.out @= Bool(s.a and (s.b or 0))

    TV_bool_and_or = [IO(), (10, 5, 1), (12, 3, 1)]
    SV_bool_and_or = "  assign __out_bits = (|a) & ((|b) | 1'h0);\n"

    def test_bool_bool(self):
        self.simulate(self.BoolAndOr(), self.TV_bool_and_or)
        self.translate(self.BoolAndOr(), self.SV_bool_and_or)

    class BitsProperties(NoBoolBit):
        @build
        def connect(s):
            # No Bool() for all Bits1
            s.out @= s.a.Z and s.b.P or s.a.N

    TV_bits_properties = [IO(), (10, 5, 1), (5, 4, 0)]
    SV_bits_properties = (
        "  assign __out_bits = a == 4'h0 & ^b | a[$bits(a) - 32'h1 +: 1];\n"
    )

    def test_bits_properties(self):
        self.simulate(self.BitsProperties(), self.TV_bits_properties)
        self.translate(self.BitsProperties(), self.SV_bits_properties)

    class CompareExpr(NoBoolBit):
        @build
        def connect(s):
            # No Bool() for all Bits1
            s.out @= s.a != 10 and s.b == 5 or s.a < s.b

    TV_compare_expr = [IO(), (10, 5, 0), (10, 3, 0), (15, 5, 1)]
    SV_compare_expr = "  assign __out_bits = a != 4'hA & b == 4'h5 | a < b;\n"

    def test_compare_expr(self):
        self.simulate(self.CompareExpr(), self.TV_compare_expr)
        self.translate(self.CompareExpr(), self.SV_compare_expr)

    class AllBits1(NoBoolBit):
        @build
        def connect(s):
            # No Bool() for all Bits1
            s.out @= s.a[0] and b1(1) or s.b[0] and TRUE

    TV_all_bits1 = [IO(), (10, 5, 1), (0, 3, 1), (8, 0, 0)]
    SV_all_bits1 = "  assign __out_bits = a[0] & 1'h1 | b[0] & 1'h1;\n"

    def test_all_bits1(self):
        self.simulate(self.AllBits1(), self.TV_all_bits1)
        self.translate(self.AllBits1(), self.SV_all_bits1)

    class AllScalar(RawModule):
        @build
        def ports(s):
            s.a = Input()
            s.b = Input()
            s.c = Input()
            s.out = Output()

        @comb
        def update(s):
            s.out /= s.a and s.b or s.c or b1(0)

    class IOScalar(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        out = Output()

    TV_all_scalar = [
        IOScalar(),
        (0, 0, 0, 0),
        (1, 1, 0, 1),
        (0, 1, 1, 1),
        (1, 0, 1, 1),
    ]
    SV_all_scalar = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = a & b | c | 1'h0;\n"
        "\n"
    )

    def test_all_scalar(self):
        self.simulate(self.AllScalar(), self.TV_all_scalar)
        self.translate(self.AllScalar(), self.SV_all_scalar)

    class ScalarInt(RawModule):
        @build
        def ports(s):
            s.a = Input()
            s.b = Input()
            s.c = Input()
            s.out = Output()

        @comb
        def update(s):
            s.out /= s.a and 1 or 0 and s.b or s.c and TRUE

    TV_scalar_int = [
        IOScalar(),
        (0, 0, 0, 0),
        (1, 0, 0, 1),
        (0, 1, 1, 1),
        (1, 1, 0, 1),
    ]
    SV_scalar_int = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = a & 1'h1 | 1'h0 & b | c & 1'h1;\n"
        "\n"
    )

    def test_scalar_int(self):
        self.simulate(self.ScalarInt(), self.TV_scalar_int)
        self.translate(self.ScalarInt(), self.SV_scalar_int)


# Boolean NOT is tested in expr_unary_test.


class TestBoolAnd(BaseTestCase):
    class BoolAnd(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit && 1-bit
            s.out44 = Output()  # 4-bit && 4-bit
            s.out14 = Output()  # 1-bit && 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output()
        out14 = Output()

    class AndVec(BoolAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a and s.in1b
            s.out44 /= Bool(s.in4a and s.in4b)
            s.out14 /= Bool(s.in1a and s.in4a)

    TV_vec = [
        IO(),
        (0, 1, 0b1010, 0b0011, 0, 1, 0),
        (1, 0, 0b1010, 0b0000, 0, 0, 1),
        (1, 1, 0b0101, 0b0011, 1, 1, 1),
    ]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a & in1b;\n"
        "    __out44_bits = (|in4a) & (|in4b);\n"
        "    __out14_bits = in1a & (|in4a);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.AndVec(), self.TV_vec)
        self.translate(self.AndVec(), self.SV_vec)

    class AndBits(BoolAnd):
        @comb
        def update(s):
            s.out11 /= b1(0) and b1(1)
            s.out44 /= Bool(b4(0b0101) and b4(0b0011))
            s.out14 /= Bool(b1(1) and b4(0b0101))

    TV_bits = [IO(), (None, None, None, None, 0, 1, 1)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 & 1'h1;\n"
        "    __out44_bits = (|(4'h5)) & (|(4'h3));\n"
        "    __out14_bits = 1'h1 & (|(4'h5));\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.AndBits(), self.TV_bits)
        self.translate(self.AndBits(), self.SV_bits)

    class AndInt(BoolAnd):
        @comb
        def update(s):
            s.out11 /= 0 and 1
            s.out44 /= Bool(5 and 3)
            s.out14 /= Bool(1 and 5)

    TV_int = [IO(), (None, None, None, None, 0, 1, 1)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0;\n"
        "    __out44_bits = 1'h1;\n"
        "    __out14_bits = 1'h1;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.AndInt(), self.TV_int)
        self.translate(self.AndInt(), self.SV_int)

    class AndIntExpr(BoolAnd):
        @comb
        def update(s):
            s.out11 /= Bool((1 + 2) and (3 - 1))
            s.out44 /= Bool((2 & 3) and (4 | 1))
            s.out14 /= Bool(-(1 + 2) and not (3 - 1))

    TV_int_expr = [IO(), (None, None, None, None, 1, 1, 0)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 1'h1;\n"
        "    __out14_bits = 1'h0;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.AndIntExpr(), self.TV_int_expr)
        self.translate(self.AndIntExpr(), self.SV_int_expr)

    class AndCompare(BoolAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a == 0 and s.in1b != 1
            s.out44 /= s.in4a <= 10 and s.in4b >= 5
            s.out14 /= s.in1a == 1 and s.in4a < 15

    TV_compare = [
        IO(),
        (0, 0, 10, 5, 1, 1, 0),
        (0, 1, 10, 3, 0, 0, 0),
        (1, 1, 15, 5, 0, 0, 0),
    ]
    SV_compare = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a == 1'h0 & in1b != 1'h1;\n"
        "    __out44_bits = in4a <= 4'hA & in4b >= 4'h5;\n"
        "    __out14_bits = (&in1a) & in4a < 4'hF;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_compare(self):
        self.simulate(self.AndCompare(), self.TV_compare)
        self.translate(self.AndCompare(), self.SV_compare)

    class AndMulti(BoolAnd):
        @comb
        def update(s):
            s.out11 /= s.in1a and b1(1) and 1 and (1 + 0)
            s.out44 /= Bool(s.in4a and b4(5) and 3 and (2 & 3))
            s.out14 /= Bool(s.in1a and b4(5) and 1 and (3 - 1))

    TV_multi = [
        IO(),
        (0, None, 0b1010, None, 0, 1, 0),
        (1, None, 0b1010, None, 1, 1, 1),
        (1, None, 0b0000, None, 1, 0, 1),
    ]
    SV_multi = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a & 1'h1 & 1'h1 & 1'h1;\n"
        "    __out44_bits = (|in4a) & (|(4'h5)) & (|(32'h3)) & (|(32'h2));\n"
        "    __out14_bits = in1a & (|(4'h5)) & 1'h1 & (|(32'h2));\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_multi(self):
        self.simulate(self.AndMulti(), self.TV_multi)
        self.translate(self.AndMulti(), self.SV_multi)


class TestBoolOr(BaseTestCase):
    class BoolOr(RawModule):
        @build
        def ports(s):
            s.in1a = Input()
            s.in1b = Input()
            s.in4a = Input(4)
            s.in4b = Input(4)
            s.out11 = Output()  # 1-bit || 1-bit
            s.out44 = Output()  # 4-bit || 4-bit
            s.out14 = Output()  # 1-bit || 4-bit

    class IO(IOStruct):
        in1a = Input()
        in1b = Input()
        in4a = Input(4)
        in4b = Input(4)
        out11 = Output()
        out44 = Output()
        out14 = Output()

    class OrVec(BoolOr):
        @comb
        def update(s):
            s.out11 /= s.in1a or s.in1b
            s.out44 /= Bool(s.in4a or s.in4b)
            s.out14 /= Bool(s.in1a or s.in4a)

    TV_vec = [
        IO(),
        (0, 0, 0b0000, 0b0000, 0, 0, 0),
        (1, 0, 0b1010, 0b0000, 1, 1, 1),
        (0, 1, 0b0000, 0b0011, 1, 1, 0),
    ]
    SV_vec = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a | in1b;\n"
        "    __out44_bits = (|in4a) | (|in4b);\n"
        "    __out14_bits = in1a | (|in4a);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_vec(self):
        self.simulate(self.OrVec(), self.TV_vec)
        self.translate(self.OrVec(), self.SV_vec)

    class OrBits(BoolOr):
        @comb
        def update(s):
            s.out11 /= b1(0) or b1(1)
            s.out44 /= Bool(b4(0b0101) or b4(0b0011))
            s.out14 /= Bool(b1(0) or b4(0b0101))

    TV_bits = [IO(), (None, None, None, None, 1, 1, 1)]
    SV_bits = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h0 | 1'h1;\n"
        "    __out44_bits = (|(4'h5)) | (|(4'h3));\n"
        "    __out14_bits = 1'h0 | (|(4'h5));\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_bits(self):
        self.simulate(self.OrBits(), self.TV_bits)
        self.translate(self.OrBits(), self.SV_bits)

    class OrInt(BoolOr):
        @comb
        def update(s):
            s.out11 /= 0 or 1
            s.out44 /= Bool(5 or 3)
            s.out14 /= Bool(0 or 5)

    TV_int = [IO(), (None, None, None, None, 1, 1, 1)]
    SV_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 1'h1;\n"
        "    __out14_bits = 1'h1;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int(self):
        self.simulate(self.OrInt(), self.TV_int)
        self.translate(self.OrInt(), self.SV_int)

    class OrIntExpr(BoolOr):
        @comb
        def update(s):
            s.out11 /= Bool((1 + 2) or (3 - 1))
            s.out44 /= Bool((2 & 3) or (4 | 1))
            s.out14 /= Bool(-(1 + 2) or not (3 - 1))

    TV_int_expr = [IO(), (None, None, None, None, 1, 1, 1)]
    SV_int_expr = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = 1'h1;\n"
        "    __out44_bits = 1'h1;\n"
        "    __out14_bits = 1'h1;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_int_expr(self):
        self.simulate(self.OrIntExpr(), self.TV_int_expr)
        self.translate(self.OrIntExpr(), self.SV_int_expr)

    class OrCompare(BoolOr):
        @comb
        def update(s):
            s.out11 /= s.in1a == 0 or s.in1b != 1
            s.out44 /= s.in4a <= 10 or s.in4b >= 5
            s.out14 /= s.in1a == 1 or s.in4a < 15

    TV_compare = [
        IO(),
        (0, 0, 10, 5, 1, 1, 1),
        (0, 1, 10, 3, 1, 1, 1),
        (1, 1, 15, 5, 0, 1, 1),
    ]
    SV_compare = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a == 1'h0 | in1b != 1'h1;\n"
        "    __out44_bits = in4a <= 4'hA | in4b >= 4'h5;\n"
        "    __out14_bits = (&in1a) | in4a < 4'hF;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_compare(self):
        self.simulate(self.OrCompare(), self.TV_compare)
        self.translate(self.OrCompare(), self.SV_compare)

    class OrMulti(BoolOr):
        @comb
        def update(s):
            s.out11 /= s.in1a or b1(0) or 0 or (1 - 1)
            s.out44 /= Bool(s.in4a or b4(0b0000) or 0 or (2 & 0))
            s.out14 /= Bool(s.in1a or b4(0b0000) or 0 or (3 ^ 3))

    TV_multi = [
        IO(),
        (0, None, 0b0000, None, 0, 0, 0),
        (1, None, 0b0000, None, 1, 0, 1),
        (0, None, 0b0101, None, 0, 1, 0),
    ]
    SV_multi = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out11_bits = in1a | 1'h0 | 1'h0 | 1'h0;\n"
        "    __out44_bits = (|in4a) | (|(4'h0)) | 1'h0 | 1'h0;\n"
        "    __out14_bits = in1a | (|(4'h0)) | 1'h0 | 1'h0;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_multi(self):
        self.simulate(self.OrMulti(), self.TV_multi)
        self.translate(self.OrMulti(), self.SV_multi)


class TestScalarComplex(BaseTestCase):
    class ScalarComplex(RawModule):
        @build
        def ports(s):
            s.a = Input()
            s.b = Input()
            s.c = Input()
            s.d = Input()
            s.e = Input()
            s.out1 = Output()
            s.out2 = Output()
            s.out3 = Output()

    class IO(IOStruct):
        a = Input()
        b = Input()
        c = Input()
        d = Input()
        e = Input()
        out1 = Output()
        out2 = Output()
        out3 = Output()

    class NestedScalarExpr(ScalarComplex):
        @comb
        def update(s):
            s.out1 /= s.a and s.b and s.c or s.d or s.e
            s.out2 /= not s.a or s.b or s.c and not s.d and s.e
            s.out3 /= s.a and not s.b or s.c and s.d or not s.e

    TV_nested_scalar = [
        IO(),
        (0, 0, 0, 0, 0, 0, 1, 1),
        (1, 1, 1, 0, 0, 1, 1, 1),
        (0, 0, 0, 1, 0, 1, 1, 1),
        (1, 0, 1, 1, 1, 1, 0, 1),
    ]
    SV_nested_scalar = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = a & b & c | d | e;\n"
        "    __out2_bits = ~a | b | c & ~d & e;\n"
        "    __out3_bits = a & ~b | c & d | ~e;\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_nested(self):
        self.simulate(self.NestedScalarExpr(), self.TV_nested_scalar)
        self.translate(self.NestedScalarExpr(), self.SV_nested_scalar)


class TestVectorComplex(BaseTestCase):
    class VectorComplex(RawModule):
        @build
        def ports(s):
            s.a = Input()
            s.b = Input(4)
            s.c = Input(4)
            s.d = Input(8)
            s.e = Input(8)
            s.out1 = Output()
            s.out2 = Output()
            s.out3 = Output()

    class IO(IOStruct):
        a = Input()
        b = Input(4)
        c = Input(4)
        d = Input(8)
        e = Input(8)
        out1 = Output()
        out2 = Output()
        out3 = Output()

    class NestedVectorExpr(VectorComplex):
        @comb
        def update(s):
            s.out1 /= Bool(s.a and s.b and s.c or s.d or s.e)
            s.out2 /= Bool(not s.a or s.b or s.c and not s.d and s.e)
            s.out3 /= Bool(s.a and not s.b or s.c and s.d or not s.e)

    TV_nested_vector = [
        IO(),
        (0, 0, 0, 0, 0, 0, 1, 1),
        (1, 1, 1, 0, 0, 1, 1, 1),
        (0, 0, 0, 1, 0, 1, 1, 1),
        (1, 0, 1, 1, 1, 1, 0, 1),
    ]
    SV_nested_vector = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = a & (|b) & (|c) | (|d) | (|e);\n"
        "    __out2_bits = ~a | (|b) | (|c) & ~(|d) & (|e);\n"
        "    __out3_bits = a & ~(|b) | (|c) & (|d) | ~(|e);\n"
        "  end // always_comb\n"
        "\n"
    )

    def test_nested(self):
        self.simulate(self.NestedVectorExpr(), self.TV_nested_vector)
        self.translate(self.NestedVectorExpr(), self.SV_nested_vector)
