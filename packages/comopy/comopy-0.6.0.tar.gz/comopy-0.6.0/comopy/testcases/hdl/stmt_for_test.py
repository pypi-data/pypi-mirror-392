# Tests for HDL statement: If
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    IOStruct,
    Logic,
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


class TestRange(BaseTestCase):
    class Loop(RawModule):
        @build
        def ports(s):
            s.data = Input(32)
            s.result = Output(32)

    class IO(IOStruct):
        data = Input(32)
        result = Output(32)

    class RangeCount(Loop):
        @comb
        def update(s):
            for i in range(32):
                s.result[i] /= s.data[i]

    TV_range_count = [IO(), (0x12345678, 0x12345678)]
    SV_range_count = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h20; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[i]\n"
        "      __result_bits[i +: 1] = data[i +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_range_count(self):
        self.simulate(self.RangeCount(), self.TV_range_count)
        self.translate(self.RangeCount(), self.SV_range_count)

    class RangeStartStop(Loop):
        @comb
        def update(s):
            for i in range(16, 32):
                s.result[i] /= s.data[i]
            for j in range(0, 16):
                s.result[j] /= s.data[16 - j - 1]

    TV_range_start_stop = [IO(), (0x12345555, 0x1234AAAA)]
    SV_range_start_stop = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h10; i < 32'h20; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[i]\n"
        "      __result_bits[i +: 1] = data[i +: 1];\n"
        "    end\n"
        "    for (logic [31:0] j = 32'h0; j < 32'h10; j += 32'h1) begin\n"
        "      // s.result[j] /= s.data[16 - j - 1]\n"
        "      __result_bits[j +: 1] = data[32'h10 - j - 32'h1 +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_range_start_stop(self):
        self.simulate(self.RangeStartStop(), self.TV_range_start_stop)
        self.translate(self.RangeStartStop(), self.SV_range_start_stop)

    class RangeStep(Loop):
        @comb
        def update(s):
            for i in range(0, 32, 2):
                s.result[i, 2] /= s.data[i, 2]

    TV_range_step = [IO(), (0x12345678, 0x12345678)]
    SV_range_step = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h20; i += 32'h2) begin\n"
        "      // s.result[i, 2] /= s.data[i, 2]\n"
        "      __result_bits[i +: 2] = data[i +: 2];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_range_step(self):
        self.simulate(self.RangeStep(), self.TV_range_step)
        self.translate(self.RangeStep(), self.SV_range_step)


class TestLoopVar(BaseTestCase):
    class Loop(RawModule):
        @build
        def ports(s):
            s.data = Input(8)
            s.result = Output(8)

    class IO(IOStruct):
        data = Input(8)
        result = Output(8)

    # = forced_i32
    class I32VarAssign(Loop):
        @comb
        def update(s):
            for i in range(4):
                s.result[i * 2, 2] /= i

    TV_i32_var_assign = [IO(), (0, 0b11100100)]
    SV_i32_var_assign = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h4; i += 32'h1) begin\n"
        "      // s.result[i * 2, 2] /= i\n"
        "      __result_bits[i * 32'h2 +: 2] = i[1:0];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_assign(self):
        self.simulate(self.I32VarAssign(), self.TV_i32_var_assign)
        self.translate(self.I32VarAssign(), self.SV_i32_var_assign)

    # UnaryOp forced_i32
    class I32VarUnary(Loop):
        @comb
        def update(s):
            s.result /= 0
            for i in range(1, 2):
                s.result[i, -2] /= ~i
                s.result[1 + i] /= not i
                s.result[2 + i] /= Bool(i)
                s.result[4 + i, -2] /= +i
                s.result[6 + i, -2] /= -i

    TV_i32_var_unary = [IO(), (None, 0b11011010)]
    SV_i32_var_unary = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __result_bits = 8'h0;\n"
        "    for (logic [31:0] i = 32'h1; i < 32'h2; i += 32'h1) begin\n"
        "      automatic logic [31:0] _GEN = ~i;\n"
        "      automatic logic [31:0] _GEN_0 = 32'h0 - i;\n"
        "      // s.result[i, -2] /= ~i\n"
        "      __result_bits[i -: 2] = _GEN[1:0];\n"
        "      // s.result[1 + i] /= not i\n"
        "      __result_bits[32'h1 + i +: 1] = ~(|i);\n"
        "      // s.result[2 + i] /= Bool(i)\n"
        "      __result_bits[32'h2 + i +: 1] = |i;\n"
        "      // s.result[4 + i, -2] /= +i\n"
        "      __result_bits[32'h4 + i -: 2] = i[1:0];\n"
        "      // s.result[6 + i, -2] /= -i\n"
        "      __result_bits[32'h6 + i -: 2] = _GEN_0[1:0];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_unary(self):
        self.simulate(self.I32VarUnary(), self.TV_i32_var_unary)
        self.translate(self.I32VarUnary(), self.SV_i32_var_unary)

    # forced_i32 + ...
    class I32VarLeft(Loop):
        @comb
        def update(s):
            s.result /= s.data
            for i in range(5):
                s.result /= i + s.result

    TV_i32_var_left = [IO(), (100, 110)]
    SV_i32_var_left = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __result_bits = data;\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h5; i += 32'h1) begin\n"
        "      __result_bits = i[7:0] + __result_bits;\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_left(self):
        self.simulate(self.I32VarLeft(), self.TV_i32_var_left)
        self.translate(self.I32VarLeft(), self.SV_i32_var_left)

    # ... + forced_i32
    class I32VarRight(Loop):
        @comb
        def update(s):
            s.result /= s.data
            for i in range(5):
                s.result /= s.result + i

    TV_i32_var_right = [IO(), (100, 110)]
    SV_i32_var_right = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __result_bits = data;\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h5; i += 32'h1) begin\n"
        "      __result_bits = __result_bits + i[7:0];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_right(self):
        self.simulate(self.I32VarRight(), self.TV_i32_var_right)
        self.translate(self.I32VarRight(), self.SV_i32_var_right)

    # ... << forced_i32
    class I32VarShamt(Loop):
        @comb
        def update(s):
            s.result /= 0
            for i in range(8):
                s.result /= s.result | (s.data[i].ext(8) << i)

    TV_i32_var_shamt = [IO(), (0xAB, 0xAB)]
    SV_i32_var_shamt = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __result_bits = 8'h0;\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h8; i += 32'h1) begin\n"
        "      __result_bits = __result_bits | {7'h0, data[i +: 1]} << i;\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_shamt(self):
        self.simulate(self.I32VarShamt(), self.TV_i32_var_shamt)
        self.translate(self.I32VarShamt(), self.SV_i32_var_shamt)

    # forced_i32 in ?:
    class I32VarCond(Loop):
        @build
        def condition(s):
            s.rev = Logic()
            s.rev @= s.data[7]

        @comb
        def update(s):
            for i in range(2):
                # condition ? forced_i32 : forced_i32
                s.result[i * 2, 2] /= i if s.rev else 3 - i
            for j in range(1):
                # condition ? forced_i32 : constant
                s.result[4 + j * 2, 2] /= j if s.rev else b2(3)
                # condition ? constant : forced_i32
                s.result[6 + j * 2, 2] /= b2(3) if s.rev else j

    TV_i32_var_cond = [
        IO(),
        (0b10101010, 0b11000100),
        (0b01010101, 0b00111011),
    ]
    SV_i32_var_cond = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h2; i += 32'h1) begin\n"
        "      automatic logic [31:0] _GEN = rev ? i : 32'h3 - i;\n"
        "      // s.result[i * 2, 2] /= i if s.rev else 3 - i\n"
        "      __result_bits[i * 32'h2 +: 2] = _GEN[1:0];\n"
        "    end\n"
        "    for (logic [31:0] j = 32'h0; j < 32'h1; j += 32'h1) begin\n"
        "      // s.result[4 + j * 2, 2] /= j if s.rev else b2(3)\n"
        "      __result_bits[32'h4 + j * 32'h2 +: 2] = rev ? j[1:0] : 2'h3;\n"
        "      // s.result[6 + j * 2, 2] /= b2(3) if s.rev else j\n"
        "      __result_bits[32'h6 + j * 32'h2 +: 2] = rev ? 2'h3 : j[1:0];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_cond(self):
        self.simulate(self.I32VarCond(), self.TV_i32_var_cond)
        self.translate(self.I32VarCond(), self.SV_i32_var_cond)

    # forced_i32 >= ...; ... != forced_i32
    class I32VarCompare(Loop):
        @comb
        def update(s):
            s.result /= 0
            for i in range(8):
                if i >= s.data:
                    s.result[i] /= 1
            for j in range(8):
                if s.data != j:
                    s.result[j] /= ~s.result[j]

    TV_i32_var_compare = [
        IO(),
        (4, 0b00011111),
        (0, 0b00000001),
        (8, 0b11111111),
    ]
    SV_i32_var_compare = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __result_bits = 8'h0;\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h8; i += 32'h1) begin\n"
        "      if (i[7:0] >= data) begin\n"
        "        // s.result[i] /= 1\n"
        "        __result_bits[i +: 1] = 1'h1;\n"
        "      end\n"
        "    end\n"
        "    for (logic [31:0] j = 32'h0; j < 32'h8; j += 32'h1) begin\n"
        "      if (data != j[7:0]) begin\n"
        "        // s.result[j] /= ~s.result[j]\n"
        "        __result_bits[j +: 1] = ~__result_bits[j +: 1];\n"
        "      end\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_compare(self):
        self.simulate(self.I32VarCompare(), self.TV_i32_var_compare)
        self.translate(self.I32VarCompare(), self.SV_i32_var_compare)


class TestLoopVarIndex(BaseTestCase):
    class Loop(RawModule):
        @build
        def ports(s):
            s.data = Input(32)
            s.result = Output(32)

    class IO(IOStruct):
        data = Input(32)
        result = Output(32)

    # [forced_i32]
    class I32VarIndex(Loop):
        @comb
        def update(s):
            for i in range(32):
                s.result[i] /= s.data[i]

    TV_i32_var_index = [IO(), (0x12345678, 0x12345678)]
    SV_i32_var_index = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h20; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[i]\n"
        "      __result_bits[i +: 1] = data[i +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index(self):
        self.simulate(self.I32VarIndex(), self.TV_i32_var_index)
        self.translate(self.I32VarIndex(), self.SV_i32_var_index)

    # [constant - forced_i32 - constant]
    class I32VarIndexSub(Loop):
        @comb
        def update(s):
            for i in range(32):
                s.result[i] /= s.data[32 - i - 1]

    TV_i32_var_index_sub = [IO(), (0x55555555, 0xAAAAAAAA)]
    SV_i32_var_index_sub = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h20; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[32 - i - 1]\n"
        "      __result_bits[i +: 1] = data[32'h20 - i - 32'h1 +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_sub(self):
        self.simulate(self.I32VarIndexSub(), self.TV_i32_var_index_sub)
        self.translate(self.I32VarIndexSub(), self.SV_i32_var_index_sub)

    # [forced_i32 + forced_i32 ...]
    class I32VarIndexAdd(Loop):
        @comb
        def update(s):
            for i in range(8):
                s.result[0 + i + i + i + i] /= s.data[28 - (i + i + i + i) + 0]
                s.result[1 + i + i + i + i] /= s.data[28 - (i + i + i + i) + 1]
                s.result[2 + i + i + i + i] /= s.data[28 - (i + i + i + i) + 2]
                s.result[3 + i + i + i + i] /= s.data[28 - (i + i + i + i) + 3]

    TV_i32_var_index_add = [IO(), (0x12345678, 0x87654321)]
    SV_i32_var_index_add = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h8; i += 32'h1) begin\n"
        "      // s.result[0 + i + i + i + i] /= "
        "s.data[28 - (i + i + i + i) + 0]\n"
        "      __result_bits[32'h0 + i + i + i + i +: 1] =\n"
        "        data[32'h1C - (i + i + i + i) + 32'h0 +: 1];\n"
        "      // s.result[1 + i + i + i + i] /= "
        "s.data[28 - (i + i + i + i) + 1]\n"
        "      __result_bits[32'h1 + i + i + i + i +: 1] =\n"
        "        data[32'h1C - (i + i + i + i) + 32'h1 +: 1];\n"
        "      // s.result[2 + i + i + i + i] /= "
        "s.data[28 - (i + i + i + i) + 2]\n"
        "      __result_bits[32'h2 + i + i + i + i +: 1] =\n"
        "        data[32'h1C - (i + i + i + i) + 32'h2 +: 1];\n"
        "      // s.result[3 + i + i + i + i] /= "
        "s.data[28 - (i + i + i + i) + 3]\n"
        "      __result_bits[32'h3 + i + i + i + i +: 1] =\n"
        "        data[32'h1C - (i + i + i + i) + 32'h3 +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_add(self):
        self.simulate(self.I32VarIndexAdd(), self.TV_i32_var_index_add)
        self.translate(self.I32VarIndexAdd(), self.SV_i32_var_index_add)

    # [forced_i32 * constant ...]
    class I32VarIndexMul(Loop):
        @comb
        def update(s):
            for i in range(8):
                s.result[0 + i * 4] /= s.data[28 - i * 4 + 0]
                s.result[1 + i * 4] /= s.data[28 - i * 4 + 1]
                s.result[2 + i * 4] /= s.data[28 - i * 4 + 2]
                s.result[3 + i * 4] /= s.data[28 - i * 4 + 3]

    TV_i32_var_index_mul = [IO(), (0x12345678, 0x87654321)]
    SV_i32_var_index_mul = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h8; i += 32'h1) begin\n"
        "      // s.result[0 + i * 4] /= s.data[28 - i * 4 + 0]\n"
        "      __result_bits[32'h0 + i * 32'h4 +: 1] = "
        "data[32'h1C - i * 32'h4 + 32'h0 +: 1];\n"
        "      // s.result[1 + i * 4] /= s.data[28 - i * 4 + 1]\n"
        "      __result_bits[32'h1 + i * 32'h4 +: 1] = "
        "data[32'h1C - i * 32'h4 + 32'h1 +: 1];\n"
        "      // s.result[2 + i * 4] /= s.data[28 - i * 4 + 2]\n"
        "      __result_bits[32'h2 + i * 32'h4 +: 1] = "
        "data[32'h1C - i * 32'h4 + 32'h2 +: 1];\n"
        "      // s.result[3 + i * 4] /= s.data[28 - i * 4 + 3]\n"
        "      __result_bits[32'h3 + i * 32'h4 +: 1] = "
        "data[32'h1C - i * 32'h4 + 32'h3 +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_mul(self):
        self.simulate(self.I32VarIndexMul(), self.TV_i32_var_index_mul)
        self.translate(self.I32VarIndexMul(), self.SV_i32_var_index_mul)

    # [-forced_i32 ...]
    class I32VarIndexNeg(Loop):
        @comb
        def update(s):
            for i in range(32):
                s.result[i] /= s.data[-i + 31]

    TV_i32_var_index_neg = [IO(), (0xAAAAAAAA, 0x55555555)]
    SV_i32_var_index_neg = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h20; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[-i + 31]\n"
        "      __result_bits[i +: 1] = data[32'h0 - i + 32'h1F +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_neg(self):
        self.simulate(self.I32VarIndexNeg(), self.TV_i32_var_index_neg)
        self.translate(self.I32VarIndexNeg(), self.SV_i32_var_index_neg)

    # [forced_i32 << constant ...]
    class I32VarIndexShift(Loop):
        @comb
        def update(s):
            for i in range(8):
                s.result[0 + (i << 2)] /= s.data[0 + (i << 2)]
                s.result[1 + (i << 2)] /= s.data[1 + (i << 2)]
                s.result[2 + (i << 2)] /= s.data[2 + (i << 2)]
                s.result[3 + (i << 2)] /= s.data[3 + (i << 2)]

    TV_i32_var_index_shift = [IO(), (0x12345678, 0x12345678)]
    SV_i32_var_index_shift = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h8; i += 32'h1) begin\n"
        "      // s.result[0 + (i << 2)] /= s.data[0 + (i << 2)]\n"
        "      __result_bits[32'h0 + (i << 32'h2) +: 1] = "
        "data[32'h0 + (i << 32'h2) +: 1];\n"
        "      // s.result[1 + (i << 2)] /= s.data[1 + (i << 2)]\n"
        "      __result_bits[32'h1 + (i << 32'h2) +: 1] = "
        "data[32'h1 + (i << 32'h2) +: 1];\n"
        "      // s.result[2 + (i << 2)] /= s.data[2 + (i << 2)]\n"
        "      __result_bits[32'h2 + (i << 32'h2) +: 1] = "
        "data[32'h2 + (i << 32'h2) +: 1];\n"
        "      // s.result[3 + (i << 2)] /= s.data[3 + (i << 2)]\n"
        "      __result_bits[32'h3 + (i << 32'h2) +: 1] = "
        "data[32'h3 + (i << 32'h2) +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_shift(self):
        self.simulate(self.I32VarIndexShift(), self.TV_i32_var_index_shift)
        self.translate(self.I32VarIndexShift(), self.SV_i32_var_index_shift)

    # [forced_i32 in ?:]
    class I32VarIndexCond(Loop):
        @build
        def condition(s):
            s.rev = Logic()
            s.rev @= s.data[31]

        @comb
        def update(s):
            for i in range(16):
                # condition ? forced_i32 : forced_i32
                s.result[i] /= s.data[31 - i if s.rev else i]
            for i in range(8):
                # condition ? forced_i32 : constant
                s.result[16 + i] /= s.data[15 - i if s.rev else 0]
                # condition ? constant : forced_i32
                s.result[24 + i] /= s.data[0 if s.rev else i]

    TV_i32_var_index_cond = [
        IO(),
        (0xAAAAAAAA, 0x00555555),
        (0x55555555, 0x55FF5555),
    ]
    SV_i32_var_index_cond = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h10; i += 32'h1) begin\n"
        "      // s.result[i] /= s.data[31 - i if s.rev else i]\n"
        "      __result_bits[i +: 1] = data[rev ? 32'h1F - i : i +: 1];\n"
        "    end\n"
        "    for (logic [31:0] i_0 = 32'h0; i_0 < 32'h8; i_0 += 32'h1) begin\n"
        "      // s.result[16 + i] /= s.data[15 - i if s.rev else 0]\n"
        "      __result_bits[32'h10 + i_0 +: 1] = "
        "data[rev ? 32'hF - i_0 : 32'h0 +: 1];\n"
        "      // s.result[24 + i] /= s.data[0 if s.rev else i]\n"
        "      __result_bits[32'h18 + i_0 +: 1] = "
        "data[rev ? 32'h0 : i_0 +: 1];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_index_cond(self):
        self.simulate(self.I32VarIndexCond(), self.TV_i32_var_index_cond)
        self.translate(self.I32VarIndexCond(), self.SV_i32_var_index_cond)


class TestNestedLoop(BaseTestCase):
    class Loop(RawModule):
        @build
        def ports(s):
            s.data = Input(32)
            s.result = Output(32)

    class IO(IOStruct):
        data = Input(32)
        result = Output(32)

    class Nested2For(Loop):
        @comb
        def update(s):
            for i in range(4):
                for j in range(8):
                    s.result[i * 8 + j] /= s.data[j]

    TV_nested_for = [IO(), (0xAB, 0xABABABAB), (0x12, 0x12121212)]
    SV_nested_for = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    for (logic [31:0] i = 32'h0; i < 32'h4; i += 32'h1) begin\n"
        "      for (logic [31:0] j = 32'h0; j < 32'h8; j += 32'h1) begin\n"
        "        // s.result[i * 8 + j] /= s.data[j]\n"
        "        __result_bits[i * 32'h8 + j +: 1] = data[j +: 1];\n"
        "      end\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_nested_for(self):
        self.simulate(self.Nested2For(), self.TV_nested_for)
        self.translate(self.Nested2For(), self.SV_nested_for)

    class I32VarShiftI32Var(Loop):
        @build
        def declare(s):
            s.tmp16 = Logic(16)
            s.result @= s.tmp16.ext(32)

        @comb
        def update(s):
            s.tmp16 /= 0
            for k in range(4):
                for i in range(4):
                    s.tmp16 /= s.tmp16 + (i << (k * 4))

    TV_i32_shift_i32 = [IO(), (None, 0x6666)]
    SV_i32_shift_i32 = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    tmp16 = 16'h0;\n"
        "    for (logic [31:0] k = 32'h0; k < 32'h4; k += 32'h1) begin\n"
        "      for (logic [31:0] i = 32'h0; i < 32'h4; i += 32'h1) begin\n"
        "        automatic logic [31:0] _GEN = i << k * 32'h4;\n"
        "        tmp16 = tmp16 + _GEN[15:0];\n"
        "      end\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_i32_var_shift_i32_var(self):
        self.simulate(self.I32VarShiftI32Var(), self.TV_i32_shift_i32)
        self.translate(self.I32VarShiftI32Var(), self.SV_i32_shift_i32)
