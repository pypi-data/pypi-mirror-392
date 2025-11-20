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


class TestIfScalar(BaseTestCase):
    class IfScalar(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.sel_hi = Input()
            s.out = Output(4)

    class IO(IOStruct):
        in_ = Input(8)
        sel_hi = Input()
        out = Output(4)

    class IfBits1(IfScalar):
        @comb
        def update(s):
            if b1(1):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_bits1 = [IO(), (0x12, None, 0x1), (0x34, None, 0x3)]
    SV_bits1 = "    if (1'h1)\n"

    def test_bits1(self):
        self.simulate(self.IfBits1(), self.TV_bits1)
        self.translate(self.IfBits1(), self.SV_bits1)

    class IfTRUE(IfScalar):
        @comb
        def update(s):
            if TRUE:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_true = [IO(), (0x12, None, 0x1), (0x34, None, 0x3)]
    SV_true = "    if (1'h1)\n"

    def test_true(self):
        self.simulate(self.IfTRUE(), self.TV_true)
        self.translate(self.IfTRUE(), self.SV_true)

    class IfIntExpr(IfScalar):
        @comb
        def update(s):
            if (1 + 2) >> 2:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_int_expr = [IO(), (0x12, None, 0x2), (0x34, None, 0x4)]
    SV_int_expr = "    if (1'h0)\n"

    def test_int_expr(self):
        self.simulate(self.IfIntExpr(), self.TV_int_expr)
        self.translate(self.IfIntExpr(), self.SV_int_expr)

    class IfScalarSignal(IfScalar):
        @comb
        def update(s):
            if s.sel_hi:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_signal = [IO(), (0x12, 0, 0x2), (0x34, 1, 0x3)]
    SV_signal = "    if (sel_hi)\n"

    def test_signal(self):
        self.simulate(self.IfScalarSignal(), self.TV_signal)
        self.translate(self.IfScalarSignal(), self.SV_signal)

    class IfScalarBool(IfScalar):
        @comb
        def update(s):
            if Bool(s.sel_hi):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_bool = [IO(), (0x12, 0, 0x2), (0x34, 1, 0x3)]
    SV_bool = "    if (sel_hi)\n"

    def test_bool(self):
        self.simulate(self.IfScalarBool(), self.TV_bool)
        self.translate(self.IfScalarBool(), self.SV_bool)

    class IfScalarEqBits1(IfScalar):
        @comb
        def update(s):
            if s.sel_hi == b1(1):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_eq_bits = [IO(), (0x12, 0, 0x2), (0x34, 1, 0x3)]
    SV_eq_bits = "    if (&sel_hi)\n"

    def test_eq_bits(self):
        self.simulate(self.IfScalarEqBits1(), self.TV_eq_bits)
        self.translate(self.IfScalarEqBits1(), self.SV_eq_bits)

    class IfScalarNeqFALSE(IfScalar):
        @comb
        def update(s):
            if s.sel_hi != FALSE:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_neq_false = [IO(), (0x12, 0, 0x2), (0x34, 1, 0x3)]
    SV_neq_false = "    if (|sel_hi)\n"

    def test_neq_false(self):
        self.simulate(self.IfScalarNeqFALSE(), self.TV_neq_false)
        self.translate(self.IfScalarNeqFALSE(), self.SV_neq_false)

    class IfScalarNeqInt(IfScalar):
        @comb
        def update(s):
            if s.sel_hi != 0:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_neq_int = [IO(), (0x12, 0, 0x2), (0x34, 1, 0x3)]
    SV_neq_int = "    if (|sel_hi)\n"

    def test_neq_int(self):
        self.simulate(self.IfScalarNeqInt(), self.TV_neq_int)
        self.translate(self.IfScalarNeqInt(), self.SV_neq_int)


class TestIfVector(BaseTestCase):
    class IfVector(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.start = Input(2)
            s.out = Output(4)
            s.start_n = Logic(2)

    class IO(IOStruct):
        in_ = Input(8)
        start = Input(2)
        out = Output(4)

    class IfBits(IfVector):
        @comb
        def update(s):
            if b8(0):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_bits = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
    ]
    SV_bits = "    if (|(8'h0))\n"

    def test_bits(self):
        self.simulate(self.IfBits(), self.TV_bits)
        self.translate(self.IfBits(), self.SV_bits)

    class IfVectorSignal(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start_n:
                s.out /= s.in_[:4]
            else:
                s.out /= s.in_[4:]

    TV_signal = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_signal = "    if (|start_n)\n"

    def test_signal(self):
        self.simulate(self.IfVectorSignal(), self.TV_signal)
        self.translate(self.IfVectorSignal(), self.SV_signal)

    class IfVectorSlice(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start_n[:]:
                s.out /= s.in_[:4]
            else:
                s.out /= s.in_[4:]

    TV_slice = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_slice = "    if (|start_n)\n"

    def test_slice(self):
        self.simulate(self.IfVectorSlice(), self.TV_slice)
        self.translate(self.IfVectorSlice(), self.SV_slice)

    class IfVectorBundle1(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if cat(s.start_n[0], s.start_n[1]):
                s.out /= s.in_[:4]
            else:
                s.out /= s.in_[4:]

    TV_bundle1 = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_bundle1 = "    if (|{start_n[0], start_n[1]})\n"

    def test_bundle1(self):
        self.simulate(self.IfVectorBundle1(), self.TV_bundle1)
        self.translate(self.IfVectorBundle1(), self.SV_bundle1)

    class IfVectorBundle2(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if cat(~s.start[0], ~s.start[1]):
                s.out /= s.in_[:4]
            else:
                s.out /= s.in_[4:]

    TV_bundle2 = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_bundle2 = "    if (|{~(start[0]), ~(start[1])})\n"

    def test_bundle2(self):
        self.simulate(self.IfVectorBundle2(), self.TV_bundle2)
        self.translate(self.IfVectorBundle2(), self.SV_bundle2)

    class IfVectorExpr(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start[0] & s.start[1]:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_expr = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_expr = "    if (start[0] & start[1])\n"

    def test_expr(self):
        self.simulate(self.IfVectorExpr(), self.TV_expr)
        self.translate(self.IfVectorExpr(), self.SV_expr)

    class IfVectorEqBits(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start == b2(3):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_eq_bits = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_eq_bits = "    if (&start)\n"

    def test_eq_bits(self):
        self.simulate(self.IfVectorEqBits(), self.TV_eq_bits)
        self.translate(self.IfVectorEqBits(), self.SV_eq_bits)

    class IfVectorEqInt(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start == 3:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_eq_int = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_eq_int = "    if (&start)\n"

    def test_eq_int(self):
        self.simulate(self.IfVectorEqInt(), self.TV_eq_int)
        self.translate(self.IfVectorEqInt(), self.SV_eq_int)

    class IfVectorGtBits(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if s.start > b2(2):
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_gt_bits = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_gt_bits = "    if (start > 2'h2)\n"

    def test_gt_bits(self):
        self.simulate(self.IfVectorGtBits(), self.TV_gt_bits)
        self.translate(self.IfVectorGtBits(), self.SV_gt_bits)

    class IfVectorLeInt(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if 3 <= s.start:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_le_int = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_le_int = "    if (2'h3 <= start)\n"

    def test_le_int(self):
        self.simulate(self.IfVectorLeInt(), self.TV_le_int)
        self.translate(self.IfVectorLeInt(), self.SV_le_int)

    class IfVectorAnd(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if (s.start != 0 and s.start != 1) and s.start != 2:
                s.out /= s.in_[4:]
            else:
                s.out /= s.in_[:4]

    TV_and = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_and = "    if ((|start) & start != 2'h1 & start != 2'h2)\n"

    def test_and(self):
        self.simulate(self.IfVectorAnd(), self.TV_and)
        self.translate(self.IfVectorAnd(), self.SV_and)

    class IfVectorOr(IfVector):
        @comb
        def update(s):
            s.start_n /= ~s.start
            if (s.start == 0 or s.start == 1) or s.start == 2:
                s.out /= s.in_[:4]
            else:
                s.out /= s.in_[4:]

    TV_or = [
        IO(),
        (0xAB, 0, 0xB),
        (0xCD, 1, 0xD),
        (0xEF, 2, 0xF),
        (0x12, 3, 0x1),
    ]
    SV_or = "    if (start == 2'h0 | start == 2'h1 | start == 2'h2)\n"

    def test_or(self):
        self.simulate(self.IfVectorOr(), self.TV_or)
        self.translate(self.IfVectorOr(), self.SV_or)


class TestIfBodies(BaseTestCase):
    class IfBodies(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.swap = Input()
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(8)
        swap = Input()
        out = Output(8)

    TV = [IO(), (0x12, 0, 0x12), (0x34, 1, 0x43)]

    class IfNoElse(IfBodies):
        @comb
        def update(s):
            s.out /= s.in_
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])

    SV_no_else = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = in_;\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "  end // always_comb\n"
    )

    def test_no_else(self):
        self.simulate(self.IfNoElse(), self.TV)
        self.translate(self.IfNoElse(), self.SV_no_else)

    class IfNoBlock(IfBodies):
        @comb
        def update(s):
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])
            else:
                s.out /= s.in_

    SV_no_block = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "    else\n"
        "      __out_bits = in_;\n"
        "  end // always_comb\n"
    )

    def test_no_block(self):
        self.simulate(self.IfNoBlock(), self.TV)
        self.translate(self.IfNoBlock(), self.SV_no_block)

    class IfThenBlock(IfBodies):
        @comb
        def update(s):
            s.out /= s.in_
            if s.swap:
                s.out[:4] /= s.in_[4:]
                s.out[4:] /= s.in_[:4]

    SV_then_block = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = in_;\n"
        "    if (swap) begin\n"
        "      // s.out[:4] /= s.in_[4:]\n"
        "      __out_bits[32'h0 +: 4] = in_[7:4];\n"
        "      // s.out[4:] /= s.in_[:4]\n"
        "      __out_bits[32'h4 +: 4] = in_[3:0];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_then_block(self):
        self.simulate(self.IfThenBlock(), self.TV)
        self.translate(self.IfThenBlock(), self.SV_then_block)

    class IfElseBlock(IfBodies):
        @comb
        def update(s):
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])
            else:
                s.out[:4] /= s.in_[:4]
                s.out[4:] /= s.in_[4:]

    SV_else_block = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "    else begin\n"
        "      // s.out[:4] /= s.in_[:4]\n"
        "      __out_bits[32'h0 +: 4] = in_[3:0];\n"
        "      // s.out[4:] /= s.in_[4:]\n"
        "      __out_bits[32'h4 +: 4] = in_[7:4];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_else_block(self):
        self.simulate(self.IfElseBlock(), self.TV)
        self.translate(self.IfElseBlock(), self.SV_else_block)

    class IfThenElseBlock(IfBodies):
        @comb
        def update(s):
            if s.swap:
                s.out[:4] /= s.in_[4:]
                s.out[4:] /= s.in_[:4]
            else:
                s.out[:4] /= s.in_[:4]
                s.out[4:] /= s.in_[4:]

    SV_then_else_block = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap) begin\n"
        "      // s.out[:4] /= s.in_[4:]\n"
        "      __out_bits[32'h0 +: 4] = in_[7:4];\n"
        "      // s.out[4:] /= s.in_[:4]\n"
        "      __out_bits[32'h4 +: 4] = in_[3:0];\n"
        "    end\n"
        "    else begin\n"
        "      // s.out[:4] /= s.in_[:4]\n"
        "      __out_bits[32'h0 +: 4] = in_[3:0];\n"
        "      // s.out[4:] /= s.in_[4:]\n"
        "      __out_bits[32'h4 +: 4] = in_[7:4];\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_then_else_block(self):
        self.simulate(self.IfThenElseBlock(), self.TV)
        self.translate(self.IfThenElseBlock(), self.SV_then_else_block)


class TestIfNested(BaseTestCase):
    class IfNested(RawModule):
        @build
        def build_all(s):
            s.in_ = Input(8)
            s.swap = Input()
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(8)
        swap = Input()
        out = Output(8)

    TV = [IO(), (0x12, 0, 0x12), (0x34, 1, 0x43)]

    class IfThenIf(IfNested):
        @comb
        def update(s):
            s.out /= s.in_
            if s.swap:
                if s.in_:
                    s.out /= cat(s.in_[:4], s.in_[4:])
                else:
                    s.out /= 0

    SV_then_if = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = in_;\n"
        "    if (swap) begin\n"
        "      if (|in_)\n"
        "        __out_bits = {in_[3:0], in_[7:4]};\n"
        "      else\n"
        "        __out_bits = 8'h0;\n"
        "    end\n"
        "  end // always_comb\n"
    )

    def test_then_if(self):
        self.simulate(self.IfThenIf(), self.TV)
        self.translate(self.IfThenIf(), self.SV_then_if)

    class IfThenIfOuterElse(IfNested):
        @comb
        def update(s):
            if s.swap:
                if s.in_:
                    s.out /= cat(s.in_[:4], s.in_[4:])
                # No inner else clause
            else:
                s.out /= s.in_

    SV_then_if_outer_else = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap) begin\n"
        "      if (|in_)\n"
        "        __out_bits = {in_[3:0], in_[7:4]};\n"
        "    end\n"
        "    else\n"
        "      __out_bits = in_;\n"
        "  end // always_comb\n"
    )

    def test_then_if_outer_else(self):
        self.simulate(self.IfThenIfOuterElse(), self.TV)
        self.translate(self.IfThenIfOuterElse(), self.SV_then_if_outer_else)

    class IfElseIfElse(IfNested):
        @comb
        def update(s):
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])
            else:
                if s.in_:
                    s.out /= s.in_
                else:
                    s.out /= 0

    SV_else_if_else = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "    else if (|in_)\n"
        "      __out_bits = in_;\n"
        "    else\n"
        "      __out_bits = 8'h0;\n"
        "  end // always_comb\n"
    )

    def test_else_if_else(self):
        self.simulate(self.IfElseIfElse(), self.TV)
        self.translate(self.IfElseIfElse(), self.SV_else_if_else)

    class IfElifElse(IfNested):
        @comb
        def update(s):
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])
            elif s.in_:
                s.out /= s.in_
            else:
                s.out /= 0

    SV_elif_else = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "    else if (|in_)\n"
        "      __out_bits = in_;\n"
        "    else\n"
        "      __out_bits = 8'h0;\n"
        "  end // always_comb\n"
    )

    def test_elif_else(self):
        self.simulate(self.IfElifElse(), self.TV)
        self.translate(self.IfElifElse(), self.SV_elif_else)

    class IfCase(IfNested):
        @comb
        def update(s):
            if s.swap:
                s.out /= cat(s.in_[:4], s.in_[4:])
            else:
                match s.in_:
                    case 0:
                        s.out /= 0
                    case _:
                        s.out /= s.in_

    SV_case = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    if (swap)\n"
        "      __out_bits = {in_[3:0], in_[7:4]};\n"
        "    else begin\n"
        "      unique case (in_)\n"
        "        8'b00000000:\n"
        "          __out_bits = 8'h0;\n"
        "        default:\n"
        "          __out_bits = in_;\n"
        "      endcase\n"
        "    end\n"
        "  end // always_comb"
    )

    def test_case(self):
        self.simulate(self.IfCase(), self.TV)
        self.translate(self.IfCase(), self.SV_case)
