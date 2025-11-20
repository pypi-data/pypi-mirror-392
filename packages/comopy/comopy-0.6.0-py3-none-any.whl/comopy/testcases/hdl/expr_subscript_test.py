# Tests for HDL expression: subscripts
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    IOStruct,
    Logic,
    Module,
    Output,
    RawModule,
    build,
    comb,
    seq,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


HALF_WIDTH = 4


class TestIndexInput(BaseTestCase):
    class IndexInput(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.sel = Input(3)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        sel = Input(3)
        out = Output()

    TV = [IO(), (0b10101100, 4, 0), (0b01010011, 4, 1)]

    class IntIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[4]

    SV_int_index = "    __out_bits = in_[4];\n"

    def test_int_index(self):
        self.simulate(self.IntIndex(), self.TV)
        self.translate(self.IntIndex(), self.SV_int_index)

    class IntExprIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[1 + 3]

    SV_int_expr_index = "    __out_bits = in_[4];\n"

    def test_int_expr_index(self):
        self.simulate(self.IntExprIndex(), self.TV)
        self.translate(self.IntExprIndex(), self.SV_int_expr_index)

    class BitsIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[b3(4)]

    SV_bits_index = "    __out_bits = in_[3'h4 +: 1];\n"

    def test_bits_index(self):
        self.simulate(self.BitsIndex(), self.TV)
        self.translate(self.BitsIndex(), self.SV_bits_index)

    class BitsExprIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[b8(1) + (b8(3) | b8(2))]

    SV_bits_expr_index = "    __out_bits = in_[8'h1 + (8'h3 | 8'h2) +: 1];\n"

    def test_bits_expr_index(self):
        self.simulate(self.BitsExprIndex(), self.TV)
        self.translate(self.BitsExprIndex(), self.SV_bits_expr_index)

    class VarIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[s.sel]

    SV_var_index = "    __out_bits = in_[sel +: 1];\n"

    def test_var_index(self):
        self.simulate(self.VarIndex(), self.TV)
        self.translate(self.VarIndex(), self.SV_var_index)

    class VarExprIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[(s.sel & b3(3)) + b3(1)]

    SV_var_expr_index = "    __out_bits = in_[(sel & 3'h3) + 3'h1 +: 1];\n"

    def test_var_expr_index(self):
        self.simulate(self.VarExprIndex(), self.TV)
        self.translate(self.VarExprIndex(), self.SV_var_expr_index)

    class GlobalIndex(IndexInput):
        @comb
        def update(s):
            s.out /= s.in_[HALF_WIDTH]

    SV_global_index = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in_[HALF_WIDTH +: 1];\n"
    )

    def test_global_index(self):
        self.simulate(self.GlobalIndex(), self.TV)
        self.translate(self.GlobalIndex(), self.SV_global_index)


class TestIndexVec(BaseTestCase):
    class IndexVec(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.sel = Input(3)
            s.out = Output()
            s.vec = Logic(8)

        @comb
        def init(s):
            s.vec /= s.in_

    class IO(IOStruct):
        in_ = Input(8)
        sel = Input(3)
        out = Output()

    TV = [IO(), (0b10101100, 4, 0), (0b01010011, 4, 1)]

    class IntIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[4]

    SV_int_index = "    __out_bits = vec[4];\n"

    def test_int_index(self):
        self.simulate(self.IntIndex(), self.TV)
        self.translate(self.IntIndex(), self.SV_int_index)

    class IntExprIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[1 + 3]

    SV_int_expr_index = "    __out_bits = vec[4];\n"

    def test_int_expr_index(self):
        self.simulate(self.IntExprIndex(), self.TV)
        self.translate(self.IntExprIndex(), self.SV_int_expr_index)

    class BitsIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[b3(4)]

    SV_bits_index = "    __out_bits = vec[3'h4 +: 1];\n"

    def test_bits_index(self):
        self.simulate(self.BitsIndex(), self.TV)
        self.translate(self.BitsIndex(), self.SV_bits_index)

    class BitsExprIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[b8(1) + (b8(3) | b8(2))]

    SV_bits_expr_index = "    __out_bits = vec[8'h1 + (8'h3 | 8'h2) +: 1];\n"

    def test_bits_expr_index(self):
        self.simulate(self.BitsExprIndex(), self.TV)
        self.translate(self.BitsExprIndex(), self.SV_bits_expr_index)

    class VarIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[s.sel]

    SV_var_index = "    __out_bits = vec[sel +: 1];\n"

    def test_var_index(self):
        self.simulate(self.VarIndex(), self.TV)
        self.translate(self.VarIndex(), self.SV_var_index)

    class VarExprIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[(s.sel & b3(3)) + b3(1)]

    SV_var_expr_index = "    __out_bits = vec[(sel & 3'h3) + 3'h1 +: 1];\n"

    def test_var_expr_index(self):
        self.simulate(self.VarExprIndex(), self.TV)
        self.translate(self.VarExprIndex(), self.SV_var_expr_index)

    class GlobalIndex(IndexVec):
        @comb
        def update(s):
            s.out /= s.vec[HALF_WIDTH]

    SV_global_index = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  logic      [7:0]  vec;\n"
        "\n"
        "  // @comb init():\n"
        "  always_comb\n"
        "    vec = in_;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = vec[HALF_WIDTH +: 1];\n"
    )

    def test_global_index(self):
        self.simulate(self.GlobalIndex(), self.TV)
        self.translate(self.GlobalIndex(), self.SV_global_index)


class TestIndexOutput(BaseTestCase):
    class IndexOutput(RawModule):
        @build
        def ports(s):
            s.in_ = Input()
            s.sel = Input(3)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input()
        sel = Input(3)
        out = Output(8)

    class IntIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[4] /= s.in_

    TV_int_index_lhs = [IO(), (1, None, 0b00010000)]
    SV_int_index_lhs = "    __out_bits[32'h4 +: 1] = in_;\n"

    def test_int_index_lhs(self):
        self.simulate(self.IntIndexLHS(), self.TV_int_index_lhs)
        self.translate(self.IntIndexLHS(), self.SV_int_index_lhs)

    class IntExprIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[1 + 3] /= s.in_

    TV_int_expr_index_lhs = [IO(), (1, None, 0b00010000)]
    SV_int_expr_index_lhs = "    __out_bits[32'h4 +: 1] = in_;\n"

    def test_int_expr_index_lhs(self):
        self.simulate(self.IntExprIndexLHS(), self.TV_int_expr_index_lhs)
        self.translate(self.IntExprIndexLHS(), self.SV_int_expr_index_lhs)

    class BitsIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[b3(4)] /= s.in_

    TV_bits_index_lhs = [IO(), (1, None, 0b00010000)]
    SV_bits_index_lhs = "    __out_bits[3'h4 +: 1] = in_;\n"

    def test_bits_index_lhs(self):
        self.simulate(self.BitsIndexLHS(), self.TV_bits_index_lhs)
        self.translate(self.BitsIndexLHS(), self.SV_bits_index_lhs)

    class BitsExprIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[b8(1) + (b8(3) | b8(2))] /= s.in_

    TV_bits_expr_index_lhs = [IO(), (1, None, 0b00010000)]
    SV_bits_expr_index_lhs = "    __out_bits[8'h1 + (8'h3 | 8'h2) +: 1] = in_;"

    def test_bits_expr_index_lhs(self):
        self.simulate(self.BitsExprIndexLHS(), self.TV_bits_expr_index_lhs)
        self.translate(self.BitsExprIndexLHS(), self.SV_bits_expr_index_lhs)

    class VarIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[s.sel] /= s.in_

    TV_var_index_lhs = [IO(), (1, 4, 0b00010000), (1, 2, 0b00000100)]
    SV_var_index_lhs = "    __out_bits[sel +: 1] = in_;\n"

    def test_var_index_lhs(self):
        self.simulate(self.VarIndexLHS(), self.TV_var_index_lhs)
        self.translate(self.VarIndexLHS(), self.SV_var_index_lhs)

    class VarExprIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(s.sel & b3(3)) + b3(1)] /= s.in_

    TV_var_expr_index_lhs = [IO(), (1, 3, 0b00010000), (1, 7, 0b00010000)]
    SV_var_expr_index_lhs = "    __out_bits[(sel & 3'h3) + 3'h1 +: 1] = in_;\n"

    def test_var_expr_index_lhs(self):
        self.simulate(self.VarExprIndexLHS(), self.TV_var_expr_index_lhs)
        self.translate(self.VarExprIndexLHS(), self.SV_var_expr_index_lhs)

    class GlobalIndexLHS(IndexOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[HALF_WIDTH] /= s.in_

    TV_global_index_lhs = [IO(), (1, None, 0b00010000)]
    SV_global_index_lhs = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = 8'h0;\n"
        "    // s.out[HALF_WIDTH] /= s.in_\n"
        "    __out_bits[HALF_WIDTH +: 1] = in_;\n"
        "  end // always_comb\n"
    )

    def test_global_index_lhs(self):
        self.simulate(self.GlobalIndexLHS(), self.TV_global_index_lhs)
        self.translate(self.GlobalIndexLHS(), self.SV_global_index_lhs)


class TestSliceInput(BaseTestCase):
    class SliceInput(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.out = Output(4)

    class IO(IOStruct):
        in_ = Input(8)
        out = Output(4)

    class IntIntSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[2:6]

    TV_int_int_slice = [IO(), (0b10101100, 0b1011)]
    SV_int_int_slice = "    __out_bits = in_[5:2];\n"

    def test_int_int_slice(self):
        self.simulate(self.IntIntSlice(), self.TV_int_int_slice)
        self.translate(self.IntIntSlice(), self.SV_int_int_slice)

    class IntExprIntExprSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[1 + 2 : 0xF & 7]

    TV_int_expr_int_expr_slice = [IO(), (0b10101100, 0b0101)]
    SV_int_expr_int_expr_slice = "    __out_bits = in_[6:3];\n"

    def test_expr_expr_slice(self):
        self.simulate(
            self.IntExprIntExprSlice(), self.TV_int_expr_int_expr_slice
        )
        self.translate(
            self.IntExprIntExprSlice(), self.SV_int_expr_int_expr_slice
        )

    class IntNoneSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[4:]

    TV_int_none_slice = [IO(), (0b10101100, 0b1010)]
    SV_int_none_slice = "    __out_bits = in_[7:4];\n"

    def test_int_none_slice(self):
        self.simulate(self.IntNoneSlice(), self.TV_int_none_slice)
        self.translate(self.IntNoneSlice(), self.SV_int_none_slice)

    class NoneIntSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[:4]

    TV_none_int_slice = [IO(), (0b10101100, 0b1100)]
    SV_none_int_slice = "    __out_bits = in_[3:0];\n"

    def test_none_int_slice(self):
        self.simulate(self.NoneIntSlice(), self.TV_none_int_slice)
        self.translate(self.NoneIntSlice(), self.SV_none_int_slice)

    class BitsBitsSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[b3(2) : b3(6)]

    TV_bits_bits_slice = [IO(), (0b10101100, 0b1011)]
    SV_bits_bits_slice = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out /= s.in_[b3(2) : b3(6)]\n"
        "    __out_bits = in_[5:2];\n"
        "  end // always_comb\n"
    )

    def test_bits_bits_slice(self):
        self.simulate(self.BitsBitsSlice(), self.TV_bits_bits_slice)
        self.translate(self.BitsBitsSlice(), self.SV_bits_bits_slice)

    class BitsExprBitsExprSlice(SliceInput):
        @comb
        def update(s):
            s.out /= s.in_[b8(1) + 1 : b8(0xE) & b8(7)]

    TV_bits_expr_bits_expr_slice = [IO(), (0b10101100, 0b1011)]
    SV_bits_expr_bits_expr_slice = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out /= s.in_[b8(1) + 1 : b8(0xE) & b8(7)]\n"
        "    __out_bits = in_[5:2];\n"
        "  end // always_comb\n"
    )

    def test_bits_expr_bits_expr_slice(self):
        self.simulate(
            self.BitsExprBitsExprSlice(), self.TV_bits_expr_bits_expr_slice
        )
        self.translate(
            self.BitsExprBitsExprSlice(), self.SV_bits_expr_bits_expr_slice
        )


class TestSliceVec(BaseTestCase):
    class SliceVec(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.out = Output(4)
            s.vec = Logic(8)

        @comb
        def init(s):
            s.vec /= s.in_

    class IO(IOStruct):
        in_ = Input(8)
        out = Output(4)

    class IntIntSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.vec[2:6]

    TV_int_int_slice = [IO(), (0b10101100, 0b1011)]
    SV_int_int_slice = "    __out_bits = vec[5:2];\n"

    def test_int_int_slice(self):
        self.simulate(self.IntIntSlice(), self.TV_int_int_slice)
        self.translate(self.IntIntSlice(), self.SV_int_int_slice)

    class IntExprIntExprSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.in_[1 + 2 : 0xF & 7]

    TV_int_expr_int_expr_slice = [IO(), (0b10101100, 0b0101)]
    SV_int_expr_int_expr_slice = "    __out_bits = in_[6:3];\n"

    def test_expr_expr_slice(self):
        self.simulate(
            self.IntExprIntExprSlice(), self.TV_int_expr_int_expr_slice
        )
        self.translate(
            self.IntExprIntExprSlice(), self.SV_int_expr_int_expr_slice
        )

    class IntNoneSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.vec[4:]

    TV_int_none_slice = [IO(), (0b10101100, 0b1010)]
    SV_int_none_slice = "    __out_bits = vec[7:4];\n"

    def test_int_none_slice(self):
        self.simulate(self.IntNoneSlice(), self.TV_int_none_slice)
        self.translate(self.IntNoneSlice(), self.SV_int_none_slice)

    class NoneIntSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.vec[:4]

    TV_none_int_slice = [IO(), (0b10101100, 0b1100)]
    SV_none_int_slice = "    __out_bits = vec[3:0];\n"

    def test_none_int_slice(self):
        self.simulate(self.NoneIntSlice(), self.TV_none_int_slice)
        self.translate(self.NoneIntSlice(), self.SV_none_int_slice)

    class BitsBitsSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.vec[b3(2) : b3(6)]

    TV_bits_bits_slice = [IO(), (0b10101100, 0b1011)]
    SV_bits_bits_slice = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out /= s.vec[b3(2) : b3(6)]\n"
        "    __out_bits = vec[5:2];\n"
        "  end // always_comb\n"
    )

    def test_bits_bits_slice(self):
        self.simulate(self.BitsBitsSlice(), self.TV_bits_bits_slice)
        self.translate(self.BitsBitsSlice(), self.SV_bits_bits_slice)

    class BitsExprBitsExprSlice(SliceVec):
        @comb
        def update(s):
            s.out /= s.vec[b8(1) + 1 : b8(0xE) & b8(7)]

    TV_bits_expr_bits_expr_slice = [IO(), (0b10101100, 0b1011)]
    SV_bits_expr_bits_expr_slice = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out /= s.vec[b8(1) + 1 : b8(0xE) & b8(7)]\n"
        "    __out_bits = vec[5:2];\n"
        "  end // always_comb\n"
    )

    def test_bits_expr_bits_expr_slice(self):
        self.simulate(
            self.BitsExprBitsExprSlice(), self.TV_bits_expr_bits_expr_slice
        )
        self.translate(
            self.BitsExprBitsExprSlice(), self.SV_bits_expr_bits_expr_slice
        )


class TestSliceOutput(BaseTestCase):
    class SliceOutput(RawModule):
        @build
        def ports(s):
            s.in_ = Input(4)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(4)
        out = Output(8)

    class IntIntSliceLHS(SliceOutput):
        @comb
        def update(s):
            s.out[2:6] /= s.in_
            s.out[0:2] /= 0
            s.out[6:8] /= 0

    TV_int_int_slice_lhs = [IO(), (0b1011, 0b00101100)]
    SV_int_int_slice_lhs = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out[2:6] /= s.in_\n"
        "    __out_bits[32'h2 +: 4] = in_;\n"
        "    // s.out[0:2] /= 0\n"
        "    __out_bits[32'h0 +: 2] = 2'h0;\n"
        "    // s.out[6:8] /= 0\n"
        "    __out_bits[32'h6 +: 2] = 2'h0;\n"
        "  end // always_comb\n"
    )

    def test_int_int_slice_lhs(self):
        self.simulate(self.IntIntSliceLHS(), self.TV_int_int_slice_lhs)
        self.translate(self.IntIntSliceLHS(), self.SV_int_int_slice_lhs)

    class IntExprIntExprSliceLHS(SliceOutput):
        @comb
        def update(s):
            s.out[1 + 2 : 0xF & 7] /= s.in_
            s.out[:3] /= 0
            s.out[7:8] /= 0

    TV_int_expr_int_expr_slice_lhs = [IO(), (0b0101, 0b00101000)]
    SV_int_expr_int_expr_slice_lhs = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out[1 + 2 : 0xF & 7] /= s.in_\n"
        "    __out_bits[32'h3 +: 4] = in_;\n"
        "    // s.out[:3] /= 0\n"
        "    __out_bits[32'h0 +: 3] = 3'h0;\n"
        "    // s.out[7:8] /= 0\n"
        "    __out_bits[32'h7 +: 1] = 1'h0;\n"
        "  end // always_comb\n"
    )

    def test_expr_expr_slice_lhs(self):
        self.simulate(
            self.IntExprIntExprSliceLHS(), self.TV_int_expr_int_expr_slice_lhs
        )
        self.translate(
            self.IntExprIntExprSliceLHS(), self.SV_int_expr_int_expr_slice_lhs
        )

    class IntNoneSliceLHS(SliceOutput):
        @comb
        def update(s):
            s.out[4:] /= s.in_
            s.out[:4] /= b4(0b1100)

    TV_int_none_slice_lhs = [IO(), (0b1011, 0b10111100)]
    SV_int_none_slice_lhs = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out[4:] /= s.in_\n"
        "    __out_bits[32'h4 +: 4] = in_;\n"
        "    // s.out[:4] /= b4(0b1100)\n"
        "    __out_bits[32'h0 +: 4] = 4'hC;\n"
        "  end // always_comb\n"
    )

    def test_int_none_slice_lhs(self):
        self.simulate(self.IntNoneSliceLHS(), self.TV_int_none_slice_lhs)
        self.translate(self.IntNoneSliceLHS(), self.SV_int_none_slice_lhs)

    class BitsBitsSliceLHS(SliceOutput):
        @comb
        def update(s):
            s.out[b3(2) : b3(6)] /= s.in_
            s.out[0:2] /= 0
            s.out[6:8] /= 0

    TV_bits_bits_slice_lhs = [IO(), (0b1011, 0b00101100)]
    SV_bits_bits_slice_lhs = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out[b3(2) : b3(6)] /= s.in_\n"
        "    __out_bits[32'h2 +: 4] = in_;\n"
        "    // s.out[0:2] /= 0\n"
        "    __out_bits[32'h0 +: 2] = 2'h0;\n"
        "    // s.out[6:8] /= 0\n"
        "    __out_bits[32'h6 +: 2] = 2'h0;\n"
        "  end // always_comb\n"
    )

    def test_bits_bits_slice_lhs(self):
        self.simulate(self.BitsBitsSliceLHS(), self.TV_bits_bits_slice_lhs)
        self.translate(self.BitsBitsSliceLHS(), self.SV_bits_bits_slice_lhs)

    class BitsExprBitsExprSliceLHS(SliceOutput):
        @comb
        def update(s):
            s.out[b8(1) + 1 : b8(0xE) & b8(7)] /= s.in_
            s.out[:2] /= 0
            s.out[6:8] /= 0

    TV_bits_expr_bits_expr_slice_lhs = [IO(), (0b1011, 0b00101100)]
    SV_bits_expr_bits_expr_slice_lhs = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    // s.out[b8(1) + 1 : b8(0xE) & b8(7)] /= s.in_\n"
        "    __out_bits[32'h2 +: 4] = in_;\n"
        "    // s.out[:2] /= 0\n"
        "    __out_bits[32'h0 +: 2] = 2'h0;\n"
        "    // s.out[6:8] /= 0\n"
        "    __out_bits[32'h6 +: 2] = 2'h0;\n"
        "  end // always_comb\n"
    )

    def test_bits_expr_bits_expr_slice_lhs(self):
        self.simulate(
            self.BitsExprBitsExprSliceLHS(),
            self.TV_bits_expr_bits_expr_slice_lhs,
        )
        self.translate(
            self.BitsExprBitsExprSliceLHS(),
            self.SV_bits_expr_bits_expr_slice_lhs,
        )


class TestPartSelInput(BaseTestCase):
    class PartSelInput(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.sel = Input(3)
            s.out = Output(4)

    class IO(IOStruct):
        in_ = Input(8)
        sel = Input(3)
        out = Output(4)

    # [int +: int]
    class IntAscInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[4, 4]

    TV_int_asc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_asc_int = "    __out_bits = in_[32'h4 +: 4];\n"

    def test_int_asc_int(self):
        self.simulate(self.IntAscInt(), self.TV_int_asc_int)
        self.translate(self.IntAscInt(), self.SV_int_asc_int)

    # [int -: int]
    class IntDescInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[(7, -4)]

    TV_int_desc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_desc_int = "    __out_bits = in_[32'h7 -: 4];\n"

    def test_int_desc_int(self):
        self.simulate(self.IntDescInt(), self.TV_int_desc_int)
        self.translate(self.IntDescInt(), self.SV_int_desc_int)

    # [int_expr +: int]
    class IntExprAscInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[1 + 3, 4]

    TV_int_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_expr_asc_int = "    __out_bits = in_[32'h4 +: 4];\n"

    def test_int_expr_asc_int(self):
        self.simulate(self.IntExprAscInt(), self.TV_int_expr_asc_int)
        self.translate(self.IntExprAscInt(), self.SV_int_expr_asc_int)

    # [bits -: int]
    class BitsDescInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[(b3(7), -4)]

    TV_bits_desc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_bits_desc_int = "    __out_bits = in_[3'h7 -: 4];\n"

    def test_bits_desc_int(self):
        self.simulate(self.BitsDescInt(), self.TV_bits_desc_int)
        self.translate(self.BitsDescInt(), self.SV_bits_desc_int)

    # [bits_expr +: int]
    class BitsExprAscInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[b8(1) + (b8(3) | b8(0)), 4, FALSE]  # FALSE=ASC

    TV_bits_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_bits_expr_asc_int = "    __out_bits = in_[8'h1 + (8'h3 | 8'h0) +: 4];\n"

    def test_bits_expr_asc_int(self):
        self.simulate(self.BitsExprAscInt(), self.TV_bits_expr_asc_int)
        self.translate(self.BitsExprAscInt(), self.SV_bits_expr_asc_int)

    # [var -: int]
    class VarDescInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[(s.sel, 4, TRUE)]  # TRUE=DESC

    TV_var_desc_int = [IO(), (0b10101100, 7, 0b1010), (0b01010011, 7, 0b0101)]
    SV_var_desc_int = "    __out_bits = in_[sel -: 4];\n"

    def test_var_desc_int(self):
        self.simulate(self.VarDescInt(), self.TV_var_desc_int)
        self.translate(self.VarDescInt(), self.SV_var_desc_int)

    # [var_expr +: int]
    class VarExprAscInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[(s.sel & b3(3)) + b3(2), 4]

    TV_var_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1011),
        (0b01010011, 4, 0b0100),
    ]
    SV_var_expr_asc_int = "    __out_bits = in_[(sel & 3'h3) + 3'h2 +: 4];\n"

    def test_var_expr_asc_int(self):
        self.simulate(self.VarExprAscInt(), self.TV_var_expr_asc_int)
        self.translate(self.VarExprAscInt(), self.SV_var_expr_asc_int)

    # [int +: int_expr]
    class IntAscIntExpr(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[4, 2 + 2, ASC]

    TV_int_asc_int_expr = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_asc_int_expr = "    __out_bits = in_[32'h4 +: 4];\n"

    def test_int_asc_int_expr(self):
        self.simulate(self.IntAscIntExpr(), self.TV_int_asc_int_expr)
        self.translate(self.IntAscIntExpr(), self.SV_int_asc_int_expr)

    # [int +: bits]
    class IntAscBits(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[4, b3(4)]

    TV_int_asc_bits = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_asc_bits = (
        "    // s.out /= s.in_[4, b3(4)]\n"
        "    __out_bits = in_[32'h4 +: 4];\n"
    )

    def test_int_asc_bits(self):
        self.simulate(self.IntAscBits(), self.TV_int_asc_bits)
        self.translate(self.IntAscBits(), self.SV_int_asc_bits)

    # [int -: bits_expr]
    class IntDescBitsExpr(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[(7, b3(2) + b3(2), DESC)]

    TV_int_desc_bits_expr = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_desc_bits_expr = (
        "    // s.out /= s.in_[(7, b3(2) + b3(2), DESC)]\n"
        "    __out_bits = in_[32'h7 -: 4];\n"
    )

    def test_int_desc_bits_expr(self):
        self.simulate(self.IntDescBitsExpr(), self.TV_int_desc_bits_expr)
        self.translate(self.IntDescBitsExpr(), self.SV_int_desc_bits_expr)

    # [global_expr +: int]
    class GlobalAscInt(PartSelInput):
        @comb
        def update(s):
            s.out /= s.in_[HALF_WIDTH - 2, 4]

    TV_global_asc_int = [
        IO(),
        (0b10101100, None, 0b1011),
        (0b01010011, None, 0b0100),
    ]
    SV_global_asc_int = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in_[HALF_WIDTH - 32'h2 +: 4];\n"
    )

    def test_var_asc_global(self):
        self.simulate(self.GlobalAscInt(), self.TV_global_asc_int)
        self.translate(self.GlobalAscInt(), self.SV_global_asc_int)


class TestPartSelVec(BaseTestCase):
    class PartSelVec(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.sel = Input(3)
            s.out = Output(4)
            s.vec = Logic(8)

        @comb
        def init(s):
            s.vec /= s.in_

    class IO(IOStruct):
        in_ = Input(8)
        sel = Input(3)
        out = Output(4)

    # [int +: int]
    class IntAscInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[4, 4]

    TV_int_asc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_asc_int = "    __out_bits = vec[32'h4 +: 4];\n"

    def test_int_asc_int(self):
        self.simulate(self.IntAscInt(), self.TV_int_asc_int)
        self.translate(self.IntAscInt(), self.SV_int_asc_int)

    # [int -: int]
    class IntDescInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[(7, -4)]

    TV_int_desc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_desc_int = "    __out_bits = vec[32'h7 -: 4];\n"

    def test_int_desc_int(self):
        self.simulate(self.IntDescInt(), self.TV_int_desc_int)
        self.translate(self.IntDescInt(), self.SV_int_desc_int)

    # [int_expr +: int]
    class IntExprAscInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[1 + 3, 4]

    TV_int_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_expr_asc_int = "    __out_bits = vec[32'h4 +: 4];\n"

    def test_int_expr_asc_int(self):
        self.simulate(self.IntExprAscInt(), self.TV_int_expr_asc_int)
        self.translate(self.IntExprAscInt(), self.SV_int_expr_asc_int)

    # [bits -: int]
    class BitsDescInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[(b3(7), -4)]

    TV_bits_desc_int = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_bits_desc_int = "    __out_bits = vec[3'h7 -: 4];\n"

    def test_bits_desc_int(self):
        self.simulate(self.BitsDescInt(), self.TV_bits_desc_int)
        self.translate(self.BitsDescInt(), self.SV_bits_desc_int)

    # [bits_expr +: int]
    class BitsExprAscInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[b8(1) + (b8(3) | b8(0)), 4, FALSE]  # FALSE=ASC

    TV_bits_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_bits_expr_asc_int = "    __out_bits = vec[8'h1 + (8'h3 | 8'h0) +: 4];\n"

    def test_bits_expr_asc_int(self):
        self.simulate(self.BitsExprAscInt(), self.TV_bits_expr_asc_int)
        self.translate(self.BitsExprAscInt(), self.SV_bits_expr_asc_int)

    # [var -: int]
    class VarDescInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[(s.sel, 4, TRUE)]  # TRUE=DESC

    TV_var_desc_int = [IO(), (0b10101100, 7, 0b1010), (0b01010011, 7, 0b0101)]
    SV_var_desc_int = "    __out_bits = vec[sel -: 4];\n"

    def test_var_desc_int(self):
        self.simulate(self.VarDescInt(), self.TV_var_desc_int)
        self.translate(self.VarDescInt(), self.SV_var_desc_int)

    # [var_expr +: int]
    class VarExprAscInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[(s.sel & b3(3)) + b3(2), 4]

    TV_var_expr_asc_int = [
        IO(),
        (0b10101100, 4, 0b1011),
        (0b01010011, 4, 0b0100),
    ]
    SV_var_expr_asc_int = "    __out_bits = vec[(sel & 3'h3) + 3'h2 +: 4];\n"

    def test_var_expr_asc_int(self):
        self.simulate(self.VarExprAscInt(), self.TV_var_expr_asc_int)
        self.translate(self.VarExprAscInt(), self.SV_var_expr_asc_int)

    # [int +: int_expr]
    class IntAscIntExpr(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[4, 2 + 2, ASC]

    TV_int_asc_int_expr = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_asc_int_expr = "    __out_bits = vec[32'h4 +: 4];\n"

    def test_int_asc_int_expr(self):
        self.simulate(self.IntAscIntExpr(), self.TV_int_asc_int_expr)
        self.translate(self.IntAscIntExpr(), self.SV_int_asc_int_expr)

    # [int +: bits]
    class IntAscBits(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[4, b3(4)]

    TV_int_asc_bits = [IO(), (0b10101100, 4, 0b1010), (0b01010011, 4, 0b0101)]
    SV_int_asc_bits = (
        "    // s.out /= s.vec[4, b3(4)]\n"
        "    __out_bits = vec[32'h4 +: 4];\n"
    )

    def test_int_asc_bits(self):
        self.simulate(self.IntAscBits(), self.TV_int_asc_bits)
        self.translate(self.IntAscBits(), self.SV_int_asc_bits)

    # [int -: bits_expr]
    class IntDescBitsExpr(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[(7, b3(2) + b3(2), DESC)]

    TV_int_desc_bits_expr = [
        IO(),
        (0b10101100, 4, 0b1010),
        (0b01010011, 4, 0b0101),
    ]
    SV_int_desc_bits_expr = (
        "    // s.out /= s.vec[(7, b3(2) + b3(2), DESC)]\n"
        "    __out_bits = vec[32'h7 -: 4];\n"
    )

    def test_int_desc_bits_expr(self):
        self.simulate(self.IntDescBitsExpr(), self.TV_int_desc_bits_expr)
        self.translate(self.IntDescBitsExpr(), self.SV_int_desc_bits_expr)

    # [global_expr +: int]
    class GlobalAscInt(PartSelVec):
        @comb
        def update(s):
            s.out /= s.vec[HALF_WIDTH - 2, 4]

    TV_global_asc_int = [
        IO(),
        (0b10101100, None, 0b1011),
        (0b01010011, None, 0b0100),
    ]
    SV_global_asc_int = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  logic      [7:0]  vec;\n"
        "\n"
        "  // @comb init():\n"
        "  always_comb\n"
        "    vec = in_;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = vec[HALF_WIDTH - 32'h2 +: 4];\n"
    )

    def test_global_asc_int(self):
        self.simulate(self.GlobalAscInt(), self.TV_global_asc_int)
        self.translate(self.GlobalAscInt(), self.SV_global_asc_int)


class TestPartSelOutput(BaseTestCase):
    class PartSelOutput(RawModule):
        @build
        def ports(s):
            s.in_ = Input(4)
            s.sel = Input(3)
            s.out = Output(8)

    class IO(IOStruct):
        in_ = Input(4)
        sel = Input(3)
        out = Output(8)

    # [int +: int]
    class IntAscIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[4, 4] /= s.in_

    TV_int_asc_int_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_asc_int_lhs = "    __out_bits[32'h4 +: 4] = in_;\n"

    def test_int_asc_int_lhs(self):
        self.simulate(self.IntAscIntLHS(), self.TV_int_asc_int_lhs)
        self.translate(self.IntAscIntLHS(), self.SV_int_asc_int_lhs)

    # [int -: int]
    class IntDescIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(7, -4)] /= s.in_

    TV_int_desc_int_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_desc_int_lhs = "    __out_bits[32'h7 -: 4] = in_;\n"

    def test_int_desc_int_lhs(self):
        self.simulate(self.IntDescIntLHS(), self.TV_int_desc_int_lhs)
        self.translate(self.IntDescIntLHS(), self.SV_int_desc_int_lhs)

    # [int_expr +: int]
    class IntExprAscIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[1 + 3, 4] /= s.in_

    TV_int_expr_asc_int_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_expr_asc_int_lhs = "    __out_bits[32'h4 +: 4] = in_;\n"

    def test_int_expr_asc_int_lhs(self):
        self.simulate(self.IntExprAscIntLHS(), self.TV_int_expr_asc_int_lhs)
        self.translate(self.IntExprAscIntLHS(), self.SV_int_expr_asc_int_lhs)

    # [bits -: int]
    class BitsDescIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(b3(7), -4)] /= s.in_

    TV_bits_desc_int_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_bits_desc_int_lhs = "    __out_bits[3'h7 -: 4] = in_;\n"

    def test_bits_desc_int_lhs(self):
        self.simulate(self.BitsDescIntLHS(), self.TV_bits_desc_int_lhs)
        self.translate(self.BitsDescIntLHS(), self.SV_bits_desc_int_lhs)

    # [bits_expr +: int]
    class BitsExprAscIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[b8(1) + (b8(3) | b8(0)), 4, FALSE] /= s.in_  # FALSE=ASC

    TV_bits_expr_asc_int_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_bits_expr_asc_int_lhs = (
        "    __out_bits[8'h1 + (8'h3 | 8'h0) +: 4] = in_;\n"
    )

    def test_bits_expr_asc_int_lhs(self):
        self.simulate(self.BitsExprAscIntLHS(), self.TV_bits_expr_asc_int_lhs)
        self.translate(self.BitsExprAscIntLHS(), self.SV_bits_expr_asc_int_lhs)

    # [var -: int]
    class VarDescIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(s.sel, 4, TRUE)] /= s.in_  # TRUE=DESC

    TV_var_desc_int_lhs = [
        IO(),
        (0b1010, 7, 0b10100000),
        (0b0101, 7, 0b01010000),
    ]
    SV_var_desc_int_lhs = "    __out_bits[sel -: 4] = in_;\n"

    def test_var_desc_int_lhs(self):
        self.simulate(self.VarDescIntLHS(), self.TV_var_desc_int_lhs)
        self.translate(self.VarDescIntLHS(), self.SV_var_desc_int_lhs)

    # [var_expr +: int]
    class VarExprAscIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(s.sel & b3(3)) + b3(2), 4] /= s.in_

    TV_var_expr_asc_int_lhs = [
        IO(),
        (0b1010, 4, 0b00101000),
        (0b0101, 4, 0b00010100),
    ]
    SV_var_expr_asc_int_lhs = (
        "    __out_bits[(sel & 3'h3) + 3'h2 +: 4] = in_;\n"
    )

    def test_var_expr_asc_int_lhs(self):
        self.simulate(self.VarExprAscIntLHS(), self.TV_var_expr_asc_int_lhs)
        self.translate(self.VarExprAscIntLHS(), self.SV_var_expr_asc_int_lhs)

    # [int +: int_expr]
    class IntAscIntExprLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[4, 2 + 2, ASC] /= s.in_

    TV_int_asc_int_expr_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_asc_int_expr_lhs = "    __out_bits[32'h4 +: 4] = in_;\n"

    def test_int_asc_int_expr_lhs(self):
        self.simulate(self.IntAscIntExprLHS(), self.TV_int_asc_int_expr_lhs)
        self.translate(self.IntAscIntExprLHS(), self.SV_int_asc_int_expr_lhs)

    # [int +: bits]
    class IntAscBitsLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[4, b3(4)] /= s.in_

    TV_int_asc_bits_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_asc_bits_lhs = (
        "    // s.out[4, b3(4)] /= s.in_\n"
        "    __out_bits[32'h4 +: 4] = in_;\n"
    )

    def test_int_asc_bits_lhs(self):
        self.simulate(self.IntAscBitsLHS(), self.TV_int_asc_bits_lhs)
        self.translate(self.IntAscBitsLHS(), self.SV_int_asc_bits_lhs)

    # [int -: bits_expr]
    class IntDescBitsExprLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[(7, b3(2) + b3(2), DESC)] /= s.in_

    TV_int_desc_bits_expr_lhs = [
        IO(),
        (0b1010, 4, 0b10100000),
        (0b0101, 4, 0b01010000),
    ]
    SV_int_desc_bits_expr_lhs = (
        "    // s.out[(7, b3(2) + b3(2), DESC)] /= s.in_\n"
        "    __out_bits[32'h7 -: 4] = in_;\n"
    )

    def test_int_desc_bits_expr_lhs(self):
        self.simulate(
            self.IntDescBitsExprLHS(), self.TV_int_desc_bits_expr_lhs
        )
        self.translate(
            self.IntDescBitsExprLHS(), self.SV_int_desc_bits_expr_lhs
        )

    # [global_expr +: int]
    class GlobalAscIntLHS(PartSelOutput):
        @comb
        def update(s):
            s.out /= 0
            s.out[HALF_WIDTH - 2, 4] /= s.in_

    TV_global_asc_int_lhs = [
        IO(),
        (0b1010, None, 0b00101000),
        (0b0101, None, 0b00010100),
    ]
    SV_global_asc_int_lhs = (
        "  // Local parameters\n"
        "  localparam [31:0] HALF_WIDTH = 4;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = 8'h0;\n"
        "    // s.out[HALF_WIDTH - 2, 4] /= s.in_\n"
        "    __out_bits[HALF_WIDTH - 32'h2 +: 4] = in_;\n"
        "  end // always_comb\n"
    )

    def test_global_asc_int_lhs(self):
        self.simulate(self.GlobalAscIntLHS(), self.TV_global_asc_int_lhs)
        self.translate(self.GlobalAscIntLHS(), self.SV_global_asc_int_lhs)


MID_INDEX = 8


class TestIndexArray(BaseTestCase):
    class IndexArray(Module):
        @build
        def ports(s):
            s.we = Input()
            s.addr = Input(4)
            s.wdata = Input(8)
            s.rdata = Output(8)
            s.mem = Logic(8) @ 16

    class IO(IOStruct):
        we = Input()
        addr = Input(4)
        wdata = Input(8)
        rdata = Output(8)

    # array[int]
    class IntIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[5]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[5] <<= s.wdata

    TV_int_index = [
        IO(),
        (1, None, 0xAB, 0xAB),
        (0, None, None, 0xAB),
        (1, None, 0xCD, 0xCD),
        (0, None, None, 0xCD),
    ]
    SV_int_index = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[32'h5];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[32'h5] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_int_index(self):
        self.simulate(self.IntIndex(), self.TV_int_index)
        self.translate(self.IntIndex(), self.SV_int_index)

    # array[int_expr]
    class IntExprIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[2 + 3]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[2 + 3] <<= s.wdata

    def test_int_expr_index(self):
        self.simulate(self.IntExprIndex(), self.TV_int_index)
        self.translate(self.IntExprIndex(), self.SV_int_index)

    # array[bits]
    class BitsIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[b4(5)]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[b4(5)] <<= s.wdata

    SV_bits_index = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[4'h5];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[4'h5] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_bits_index(self):
        self.simulate(self.BitsIndex(), self.TV_int_index)
        self.translate(self.BitsIndex(), self.SV_bits_index)

    # array[bits_expr]
    class BitsExprIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[b8(2) + b8(3)]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[b8(2) + b8(3)] <<= s.wdata

    SV_bits_expr_index = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[8'h2 + 8'h3];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[8'h2 + 8'h3] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_bits_expr_index(self):
        self.simulate(self.BitsExprIndex(), self.TV_int_index)
        self.translate(self.BitsExprIndex(), self.SV_bits_expr_index)

    # array[var]
    class VarIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[s.addr]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[s.addr] <<= s.wdata

    TV_var_index = [
        IO(),
        (1, 5, 0xAB, 0xAB),
        (0, 5, None, 0xAB),
        (1, 7, 0xCD, 0xCD),
        (0, 7, None, 0xCD),
    ]
    SV_var_index = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[addr];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[addr] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_var_index(self):
        self.simulate(self.VarIndex(), self.TV_var_index)
        self.translate(self.VarIndex(), self.SV_var_index)

    # array[var_expr]
    class VarExprIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[(s.addr & b4(0xF)) + b4(1)]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[(s.addr & b4(0xF)) - b4(1)] <<= s.wdata

    TV_var_expr_index = [
        IO(),
        (1, 4, 0xAB, None),
        (0, 2, None, 0xAB),
        (1, 6, 0xCD, None),
        (0, 4, None, 0xCD),
    ]
    SV_var_expr_index = (
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[(addr & 4'hF) + 4'h1];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[(addr & 4'hF) - 4'h1] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_var_expr_index(self):
        self.simulate(self.VarExprIndex(), self.TV_var_expr_index)
        self.translate(self.VarExprIndex(), self.SV_var_expr_index)

    # array[global]
    class GlobalIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[MID_INDEX]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[MID_INDEX] <<= s.wdata

    TV_global_index = [
        IO(),
        (1, None, 0xAB, 0xAB),
        (0, None, None, 0xAB),
        (1, None, 0xCD, 0xCD),
        (0, None, None, 0xCD),
    ]
    SV_global_index = (
        "  // Local parameters\n"
        "  localparam [31:0] MID_INDEX = 8;\n"
        "\n"
        "  logic      [7:0]  mem[0:15];\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[MID_INDEX];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[MID_INDEX] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_global_index(self):
        self.simulate(self.GlobalIndex(), self.TV_global_index)
        self.translate(self.GlobalIndex(), self.SV_global_index)

    # array[global_expr]
    class GlobalExprIndex(IndexArray):
        @comb
        def update(s):
            s.rdata /= s.mem[MID_INDEX - 2]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[MID_INDEX - 2] <<= s.wdata

    SV_global_expr_index = (
        "  // Local parameters\n"
        "  localparam [31:0] MID_INDEX = 8;\n"
        "\n"
        "  logic      [7:0]  mem[0:15];\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __rdata_bits = mem[MID_INDEX - 32'h2];\n"
        "\n"
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we)\n"
        "      mem[MID_INDEX - 32'h2] <= wdata;\n"
        "  end // always @(posedge)\n"
    )

    def test_global_expr_index(self):
        self.simulate(self.GlobalExprIndex(), self.TV_global_index)
        self.translate(self.GlobalExprIndex(), self.SV_global_expr_index)
