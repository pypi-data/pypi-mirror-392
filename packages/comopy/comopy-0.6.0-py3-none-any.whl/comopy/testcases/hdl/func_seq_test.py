# Tests for HDL @seq function
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
    seq,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestRawEdge(BaseTestCase):
    class Shifter(RawModule):
        @build
        def ports(s):
            s.clk = Input()
            s.rst_n = Input()
            s.data_in = Input(8)
            s.data_out = Output(8)

        @build
        def declare(s):
            s.stage1 = Logic(8)
            s.stage2 = Logic(8)

    class IO(IOStruct):
        clk = Input()
        rst_n = Input()
        data_in = Input(8)
        data_out = Output(8)

    class PosedgeShifter(Shifter):
        @seq
        def shift(s, posedge="clk"):
            s.stage1 <<= s.data_in
            s.stage2 <<= s.stage1
            s.data_out <<= s.stage2

    TV_posedge = [
        IO(),
        (0, 1, 0xAA, None),
        (1, 1, 0xAA, None),
        (0, 1, 0xBB, None),
        (1, 1, 0xBB, None),
        (0, 1, 0xCC, None),
        (1, 1, 0xCC, 0xAA),
        (0, 1, 0xDD, 0xAA),
        (1, 1, 0xDD, 0xBB),
        (0, 1, 0x00, 0xBB),
        (1, 1, 0x00, 0xCC),
        (0, 1, 0x00, 0xCC),
        (1, 1, 0x00, 0xDD),
        (0, 1, 0x00, 0xDD),
    ]
    SV_posedge = (
        "  // @seq shift():\n"
        "  always @(posedge clk) begin\n"
        "    stage1 <= data_in;\n"
        "    stage2 <= stage1;\n"
        "    __data_out_bits <= stage2;\n"
        "  end // always @(posedge)\n"
    )

    def test_posedge(self):
        self.simulate(self.PosedgeShifter(), self.TV_posedge)
        self.translate(self.PosedgeShifter(), self.SV_posedge)

    class NegedgeShifter(Shifter):
        @seq
        def shift(s, negedge="clk"):
            s.stage1 <<= s.data_in
            s.stage2 <<= s.stage1
            s.data_out <<= s.stage2

    TV_negedge = [
        IO(),
        (1, 1, 0xAA, None),
        (0, 1, 0xAA, None),
        (1, 1, 0xBB, None),
        (0, 1, 0xBB, None),
        (1, 1, 0xCC, None),
        (0, 1, 0xCC, 0xAA),
        (1, 1, 0xDD, 0xAA),
        (0, 1, 0xDD, 0xBB),
        (1, 1, 0x00, 0xBB),
        (0, 1, 0x00, 0xCC),
        (1, 1, 0x00, 0xCC),
        (0, 1, 0x00, 0xDD),
        (1, 1, 0x00, 0xDD),
    ]
    SV_negedge = (
        "  // @seq shift():\n"
        "  always @(negedge clk) begin\n"
        "    stage1 <= data_in;\n"
        "    stage2 <= stage1;\n"
        "    __data_out_bits <= stage2;\n"
        "  end // always @(negedge)\n"
    )

    def test_negedge(self):
        self.simulate(self.NegedgeShifter(), self.TV_negedge)
        self.translate(self.NegedgeShifter(), self.SV_negedge)

    class ClockResetShifter(Shifter):
        @seq
        def shift(s, posedge="clk", negedge="rst_n"):
            if ~s.rst_n:
                s.stage1 <<= 0
                s.stage2 <<= 0
                s.data_out <<= 0
            else:
                s.stage1 <<= s.data_in
                s.stage2 <<= s.stage1
                s.data_out <<= s.stage2

    TV_clk_rst = [
        IO(),
        (0, 0, 0xAA, None),
        (1, 0, 0xAA, 0),
        (0, 0, 0xBB, 0),
        (1, 0, 0xBB, 0),
        (0, 1, 0xCC, 0),
        (1, 1, 0xCC, 0),
        (0, 1, 0xDD, 0),
        (1, 1, 0xDD, 0),
        (0, 1, 0xEE, 0),
        (1, 1, 0xEE, 0xCC),
        (0, 1, 0xFF, 0xCC),
        (1, 1, 0xFF, 0xDD),
        (0, 1, 0x00, 0xDD),
        (1, 1, 0x00, 0xEE),
    ]
    SV_clk_rst = (
        "  // @seq shift():\n"
        "  always @(posedge clk or negedge rst_n) begin\n"
        "    if (~rst_n) begin\n"
        "      stage1 <= 8'h0;\n"
        "      stage2 <= 8'h0;\n"
        "      __data_out_bits <= 8'h0;\n"
        "    end\n"
        "    else begin\n"
        "      stage1 <= data_in;\n"
        "      stage2 <= stage1;\n"
        "      __data_out_bits <= stage2;\n"
        "    end\n"
        "  end // always @(posedge, negedge)\n"
    )

    def test_clk_rst(self):
        self.simulate(self.ClockResetShifter(), self.TV_clk_rst)
        self.translate(self.ClockResetShifter(), self.SV_clk_rst)

    class BothEdgeShifter(Shifter):
        @seq
        def shift(s, posedge="clk", negedge="clk"):
            s.stage1 <<= s.data_in
            s.stage2 <<= s.stage1
            s.data_out <<= s.stage2

    TV_bothedge = [
        IO(),
        (0, 1, None, None),
        (0, 1, 0xAA, None),  # set up data
        (1, 1, 0xAA, None),  # posedge: stage1=0xAA
        (1, 1, 0xBB, None),  # set up data
        (0, 1, 0xBB, None),  # negedge: stage1=0xBB, stage2=0xAA
        (0, 1, 0xCC, None),  # set up data
        (1, 1, 0xCC, 0xAA),  # posedge: stage1=0xCC, stage2=0xBB, data_out=0xAA
        (1, 1, 0xDD, 0xAA),  # set up data
        (0, 1, 0xDD, 0xBB),  # negedge: stage1=0xDD, stage2=0xCC, data_out=0xBB
        (0, 1, 0x00, 0xBB),  # set up data
        (1, 1, 0x00, 0xCC),  # posedge: stage1=0x00, stage2=0xDD, data_out=0xCC
        (1, 1, 0x11, 0xCC),  # set up data
        (0, 1, 0x11, 0xDD),  # negedge: stage1=0x11, stage2=0x00, data_out=0xDD
        (0, 1, None, 0xDD),  # hold clk=0
    ]
    SV_bothedge = (
        "  // @seq shift():\n"
        "  always @(posedge clk or negedge clk) begin\n"
        "    stage1 <= data_in;\n"
        "    stage2 <= stage1;\n"
        "    __data_out_bits <= stage2;\n"
        "  end // always @(posedge, negedge)\n"
    )

    def test_bothedge(self):
        self.simulate(self.BothEdgeShifter(), self.TV_bothedge)
        self.translate(self.BothEdgeShifter(), self.SV_bothedge)


class TestClkEdge(BaseTestCase):
    class Shifter(Module):
        @build
        def ports(s):
            s.rst_n = Input()
            s.data_in = Input(8)
            s.data_out = Output(8)

        @build
        def declare(s):
            s.stage1 = Logic(8)
            s.stage2 = Logic(8)

    class IO(IOStruct):
        rst_n = Input()
        data_in = Input(8)
        data_out = Output(8)

    class PosedgeShifter(Shifter):
        @seq
        def shift(s):
            s.stage1 <<= s.data_in
            s.stage2 <<= s.stage1
            s.data_out <<= s.stage2

    TV_posedge = [
        IO(),
        (1, 0xAA, None),
        (1, 0xBB, None),
        (1, 0xCC, 0xAA),
        (1, 0xDD, 0xBB),
        (1, 0x00, 0xCC),
        (1, 0x00, 0xDD),
        (1, 0x00, 0x00),
    ]
    SV_posedge = (
        "  // @seq shift():\n"
        "  always @(posedge clk) begin\n"
        "    stage1 <= data_in;\n"
        "    stage2 <= stage1;\n"
        "    __data_out_bits <= stage2;\n"
        "  end // always @(posedge)\n"
    )

    def test_posedge(self):
        self.simulate(self.PosedgeShifter(), self.TV_posedge)
        self.translate(self.PosedgeShifter(), self.SV_posedge)

    class ClockResetShifter(Shifter):
        @seq
        def shift(s, negedge="rst_n"):
            if ~s.rst_n:
                s.stage1 <<= 0
                s.stage2 <<= 0
                s.data_out <<= 0
            else:
                s.stage1 <<= s.data_in
                s.stage2 <<= s.stage1
                s.data_out <<= s.stage2

    TV_clk_rst = [
        IO(),
        (1, 0xAA, None),
        (0, 0xAA, 0),  # hold data for reset
        (0, 0xBB, 0),
        (1, 0xCC, 0),
        (1, 0xDD, 0),
        (1, 0xEE, 0xCC),
        (1, 0xFF, 0xDD),
        (1, 0x11, 0xEE),
        (1, 0x22, 0xFF),
        (0, 0x22, 0),  # hold data for reset
        (0, 0x33, 0),
        (1, 0x44, 0),
    ]
    SV_clk_rst = (
        "  // @seq shift():\n"
        "  always @(posedge clk or negedge rst_n) begin\n"
        "    if (~rst_n) begin\n"
        "      stage1 <= 8'h0;\n"
        "      stage2 <= 8'h0;\n"
        "      __data_out_bits <= 8'h0;\n"
        "    end\n"
        "    else begin\n"
        "      stage1 <= data_in;\n"
        "      stage2 <= stage1;\n"
        "      __data_out_bits <= stage2;\n"
        "    end\n"
        "  end // always @(posedge, negedge)\n"
    )

    def test_clk_rst(self):
        self.simulate(self.ClockResetShifter(), self.TV_clk_rst)
        self.translate(self.ClockResetShifter(), self.SV_clk_rst)
