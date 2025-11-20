# Tests for HDL structural element: array
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    IOStruct,
    Module,
    Output,
    build,
    comb,
    seq,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestArray1D(BaseTestCase):
    class Array1D(Module):
        @build
        def ports(s):
            s.we = Input()
            s.addr = Input(4)
            s.wdata = Input(8)
            s.rdata = Output(8)

    class IO(IOStruct):
        we = Input()
        addr = Input(4)
        wdata = Input(8)
        rdata = Output(8)

    class ReadWrite(Array1D):
        @build
        def build_mem(s):
            s.mem = Logic(8) @ 16

        @comb
        def update(s):
            s.rdata /= s.mem[s.addr]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[s.addr] <<= s.wdata

    TV_read_write = [
        IO(),
        (1, 0, 0xAB, None),
        (0, 0, 0, 0xAB),
        (1, 8, 0xCD, None),
        (0, 8, 0, 0xCD),
        (1, 15, 0xEF, None),
        (0, 15, 0, 0xEF),
    ]
    SV_read_write = (
        "  // Variables for output ports\n"
        "  logic [7:0] __rdata_bits;\n"
        "\n"
        "  logic [7:0] mem[0:15];\n"
        "\n"
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

    def test_read_write(self):
        self.simulate(self.ReadWrite(), self.TV_read_write)
        self.translate(self.ReadWrite(), self.SV_read_write)

    # comb.concat requires sv.read_inout after sv.array_index_inout
    class ConcatElems(Array1D):
        @build
        def build_mem(s):
            s.mem1 = Logic(4) @ 16
            s.mem2 = Logic(4) @ 16
            s.rdata @= cat(s.mem2[s.addr], s.mem1[s.addr])

        @seq
        def update_ff(s):
            if s.we:
                s.mem1[s.addr] <<= s.wdata[:4]
                s.mem2[s.addr] <<= s.wdata[4:]

    SV_concat_elems = "  assign __rdata_bits = {mem2[addr], mem1[addr]};\n"

    def test_concat_elems(self):
        self.simulate(self.ConcatElems(), self.TV_read_write)
        self.translate(self.ConcatElems(), self.SV_concat_elems)

    class ElemSubscript(Array1D):
        @build
        def build_all(s):
            s.mem = Logic(8) @ 16
            s.sign = Logic()
            s.high = Logic(4)
            s.low = Logic(4)
            s.sign @= s.mem[s.addr][7]
            s.high @= s.mem[s.addr][7, -4]
            s.low @= s.mem[s.addr][:4]
            s.rdata @= cat(s.low, s.high) if s.sign else cat(s.high, s.low)

        @seq
        def update_ff(s):
            if s.we:
                s.mem[s.addr] <<= s.wdata

    TV_elem_subscript = [
        IO(),
        (1, 0, 0x78, None),
        (0, 0, 0, 0x78),
        (1, 8, 0x9A, None),
        (0, 8, 0, 0xA9),
        (1, 15, 0xBC, None),
        (0, 15, 0, 0xCB),
    ]
    SV_elem_subscript = (
        "  assign sign = mem[addr][7];\n"
        "  assign high = mem[addr][32'h7 -: 4];\n"
        "  assign low = mem[addr][3:0];\n"
        "  assign __rdata_bits = sign ? {low, high} : {high, low};\n"
    )

    def test_elem_subscript(self):
        self.simulate(self.ElemSubscript(), self.TV_elem_subscript)
        self.translate(self.ElemSubscript(), self.SV_elem_subscript)

    class ElemSubscriptLHS(Array1D):
        @build
        def build_all(s):
            s.mem = Logic(8) @ 16
            s.rdata @= s.mem[s.addr]

        @seq
        def update_ff(s):
            if s.we:
                s.mem[s.addr][7] <<= s.wdata[7]
                s.mem[s.addr][6, -3] <<= s.wdata[6, -3]
                s.mem[s.addr][:4] <<= s.wdata[:4]

    SV_elem_subscript_lhs = (
        "  // @seq update_ff():\n"
        "  always @(posedge clk) begin\n"
        "    if (we) begin\n"
        "      // s.mem[s.addr][7] <<= s.wdata[7]\n"
        "      mem[addr][32'h7 +: 1] <= wdata[7];\n"
        "      // s.mem[s.addr][6, -3] <<= s.wdata[6, -3]\n"
        "      mem[addr][32'h6 -: 3] <= wdata[32'h6 -: 3];\n"
        "      // s.mem[s.addr][:4] <<= s.wdata[:4]\n"
        "      mem[addr][32'h0 +: 4] <= wdata[3:0];\n"
        "    end\n"
        "  end // always @(posedge)\n"
    )

    def test_elem_subscript_lhs(self):
        self.simulate(self.ElemSubscriptLHS(), self.TV_read_write)
        self.translate(self.ElemSubscriptLHS(), self.SV_elem_subscript_lhs)
