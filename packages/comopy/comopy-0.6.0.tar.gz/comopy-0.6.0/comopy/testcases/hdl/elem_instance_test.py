# Tests for HDL structural element: module instance
#

import pytest

from comopy import *
from comopy import (  # for type checking
    DESC,
    BaseTestCase,
    Input,
    IOStruct,
    Output,
    RawModule,
    SimulatorConfig,
    build,
    comb,
)

# Test with different simulator types
sim_types = [
    SimulatorConfig.scheduled(),
    SimulatorConfig.event(),
    SimulatorConfig.auto(),
]


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True, params=sim_types)
def with_comopy_context(request):
    with comopy_context(ir_config=IRConfig.debug(), sim_config=request.param):
        yield


class Add8(RawModule):
    @build
    def build_all(s):
        s.a = Input(8)
        s.b = Input(8)
        s.cin = Input()
        s.sum = Output(8)
        s.cout = Output()

    @comb
    def add(s):
        cat(s.cout, s.sum)[:] /= (
            cat(b1(0), s.a) + cat(b1(0), s.b) + cat(b8(0), s.cin)
        )


class Passthrough(RawModule):
    @build
    def build_all(s):
        s.in_ = Input(16)
        s.out = Output(16)
        s.out @= s.in_


class TestModuleConn(BaseTestCase):
    class ModuleConn(RawModule):
        @build
        def ports(s):
            s.in1 = Input(16)
            s.in2 = Input(16)
            s.sum = Output(16)
            s.cout = Output()

    class IO(IOStruct):
        in1 = Input(16)
        in2 = Input(16)
        sum = Output(16)
        cout = Output()

    class ConnectByOrder(ModuleConn):
        @build
        def build_all(s):
            s.a = Logic(8)
            s.b = Logic(8)
            s.cin = Logic()
            s.sum8 = Logic(8)
            s.a @= s.in1[:8]
            s.b @= s.in2[:8]
            s.cin @= 0
            s.sum @= cat(b8(0), s.sum8)

            s.lo_adder = Add8(s.a, s.b, s.cin, s.sum8, s.cout)

    TV_add8 = [
        IO(),
        # Basic cases: 0 + 0 = 0
        (0x0000, 0x0000, 0x0000, 0),
        # Small numbers: 1 + 2 = 3
        (0x0001, 0x0002, 0x0003, 0),
        # Medium numbers: 85 + 102 = 187
        (0x0055, 0x0066, 0x00BB, 0),
        # Boundary case: 127 + 1 = 128 (no overflow)
        (0x007F, 0x0001, 0x0080, 0),
        # Overflow case: 128 + 128 = 0 (with carry)
        (0x0080, 0x0080, 0x0000, 1),
        # Overflow case: 255 + 1 = 0 (with carry)
        (0x00FF, 0x0001, 0x0000, 1),
        # Maximum overflow: 255 + 255 = 254 (with carry)
        (0x00FF, 0x00FF, 0x00FE, 1),
    ]
    SV_by_order = (
        "  // s.lo_adder = Add8(s.a, s.b, s.cin, s.sum8, s.cout)\n"
        "  Add8 lo_adder (\n"
        "    .a    (a),\n"
        "    .b    (b),\n"
        "    .cin  (cin),\n"
        "    .sum  (sum8),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
    )

    def test_connect_by_order(self):
        self.simulate(self.ConnectByOrder(), self.TV_add8)
        self.translate(self.ConnectByOrder(), self.SV_by_order)

    class ConnectByName(ModuleConn):
        @build
        def build_all(s):
            s.a = Logic(8)
            s.b = Logic(8)
            s.cin = Logic()
            s.sum8 = Logic(8)
            s.a @= s.in1[:8]
            s.b @= s.in2[:8]
            s.cin @= 0
            s.sum @= cat(b8(0), s.sum8)

            s.lo_adder = Add8(sum=s.sum8, a=s.a, b=s.b, cin=s.cin, cout=s.cout)

    SV_by_name = (
        "  // s.lo_adder = Add8(sum=s.sum8, a=s.a, b=s.b, cin=s.cin, "
        "cout=s.cout)\n"
        "  Add8 lo_adder (\n"
        "    .a    (a),\n"
        "    .b    (b),\n"
        "    .cin  (cin),\n"
        "    .sum  (sum8),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
    )

    def test_connect_by_name(self):
        self.simulate(self.ConnectByName(), self.TV_add8)
        self.translate(self.ConnectByName(), self.SV_by_name)

    class ConnectInt(ModuleConn):
        @build
        def build_all(s):
            s.a = Logic(8)
            s.b = Logic(8)
            s.sum8 = Logic(8)
            s.a @= s.in1[:8]
            s.b @= s.in2[:8]
            s.sum @= cat(b8(0), s.sum8)

            s.lo_adder = Add8(a=s.a, b=s.b, cin=0, sum=s.sum8, cout=s.cout)

    SV_int = (
        "  // s.lo_adder = Add8(a=s.a, b=s.b, cin=0, sum=s.sum8, "
        "cout=s.cout)\n"
        "  Add8 lo_adder (\n"
        "    .a    (a),\n"
        "    .b    (b),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (sum8),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
    )

    def test_connect_int(self):
        self.simulate(self.ConnectInt(), self.TV_add8)
        self.translate(self.ConnectInt(), self.SV_int)

    class ConnectIndex(ModuleConn):
        @build
        def build_all(s):
            s.couts = Logic(2)
            s.lo_adder = Add8(cin=0, cout=s.couts[0])
            s.lo_adder.a @= s.in1[:8]
            s.lo_adder.b @= s.in2[:8]
            s.sum @= cat(b8(0), s.lo_adder.sum)
            s.couts[1] @= 0  # unused
            s.cout @= s.couts[0]

    SV_index = (
        "  // s.lo_adder = Add8(cin=0, cout=s.couts[0])\n"
        "  logic [7:0]  _lo_adder_a;\n"
        "  logic [7:0]  _lo_adder_b;\n"
        "  Add8 lo_adder (\n"
        "    .a    (_lo_adder_a),\n"
        "    .b    (_lo_adder_b),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (_lo_adder_sum),\n"
        "    .cout (couts[32'h0 +: 1])\n"
        "  );\n"
    )

    def test_connect_index(self):
        self.simulate(self.ConnectIndex(), self.TV_add8)
        self.translate(self.ConnectIndex(), self.SV_index)

    class ConnectSlice(ModuleConn):
        @build
        def build_all(s):
            s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0, s.sum[:8])
            s.sum[8:] @= 0
            s.cout @= s.lo_adder.cout

    SV_slice = (
        "  // s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0, s.sum[:8])\n"
        "  Add8 lo_adder (\n"
        "    .a    (in1[7:0]),\n"
        "    .b    (in2[7:0]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (__sum_bits[32'h0 +: 8]),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  // s.sum[8:] @= 0\n"
        "  assign __sum_bits[32'h8 +: 8] = 8'h0;\n"
    )

    def test_connect_slice(self):
        self.simulate(self.ConnectSlice(), self.TV_add8)
        self.translate(self.ConnectSlice(), self.SV_slice)

    class ConnectPartSel(ModuleConn):
        @build
        def build_all(s):
            s.lo_adder = Add8(s.in1[0, 8], s.in2[7, -8], 0, s.sum[7, 8, DESC])
            s.sum[8:] @= 0
            s.cout @= s.lo_adder.cout

    SV_part_sel = (
        "  // s.lo_adder = Add8(s.in1[0, 8], s.in2[7, -8], 0, "
        "s.sum[7, 8, DESC])\n"
        "  Add8 lo_adder (\n"
        "    .a    (in1[32'h0 +: 8]),\n"
        "    .b    (in2[32'h7 -: 8]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (__sum_bits[32'h7 -: 8]),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
    )

    def test_connect_part_sel(self):
        self.simulate(self.ConnectPartSel(), self.TV_add8)
        self.translate(self.ConnectPartSel(), self.SV_part_sel)

    class ConnectPortPart(ModuleConn):
        @build
        def build_all(s):
            s.pass1 = Passthrough(s.in1)
            s.pass2 = Passthrough(s.in2)
            s.lo_adder = Add8(s.pass1.out[:8], s.pass2.out[0, 8], 0, s.sum[:8])
            s.sum[8:] @= 0
            s.cout @= s.lo_adder.cout

    SV_port_part = (
        "  logic        __cout_bits;\n"
        "\n"
        "  // s.pass1 = Passthrough(s.in1)\n"
        "  Passthrough pass1 (\n"
        "    .in_ (in1),\n"
        "    .out (_pass1_out)\n"
        "  );\n"
        "\n"
        "  // s.pass2 = Passthrough(s.in2)\n"
        "  Passthrough pass2 (\n"
        "    .in_ (in2),\n"
        "    .out (_pass2_out)\n"
        "  );\n"
        "\n"
        "  // s.lo_adder = Add8(s.pass1.out[:8], s.pass2.out[0, 8], "
        "0, s.sum[:8])\n"
        "  Add8 lo_adder (\n"
        "    .a    (_pass1_out[7:0]),\n"
        "    .b    (_pass2_out[32'h0 +: 8]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (__sum_bits[32'h0 +: 8]),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  // s.sum[8:] @= 0\n"
        "  assign __sum_bits[32'h8 +: 8] = 8'h0;\n"
    )

    def test_connect_port_slice(self):
        self.simulate(self.ConnectPortPart(), self.TV_add8)
        self.translate(self.ConnectPortPart(), self.SV_port_part)


class TestModuleAutoWires(BaseTestCase):
    class ModuleAutoWires(RawModule):
        @build
        def ports(s):
            s.in1 = Input(16)
            s.in2 = Input(16)
            s.sum = Output(16)
            s.cout = Output()

    class IO(IOStruct):
        in1 = Input(16)
        in2 = Input(16)
        sum = Output(16)
        cout = Output()

    class AllAutoWires(ModuleAutoWires):
        @build
        def build_all(s):
            s.lo_adder = Add8()
            s.hi_adder = Add8()

            s.lo_adder.a @= s.in1[:8]
            s.lo_adder.b @= s.in2[:8]
            s.lo_adder.cin @= 0
            s.sum[:8] @= s.lo_adder.sum
            s.hi_adder.a @= s.in1[8:]
            s.hi_adder.b @= s.in2[8:]
            s.hi_adder.cin @= s.lo_adder.cout
            s.sum[8:] @= s.hi_adder.sum
            s.cout @= s.hi_adder.cout

    TV_add16 = [
        IO(),
        # Basic cases: 0 + 0 = 0
        (0x0000, 0x0000, 0x0000, 0),
        # Small numbers: 1 + 2 = 3
        (0x0001, 0x0002, 0x0003, 0),
        # Medium numbers: 0x1234 + 0x5678 = 0x68AC
        (0x1234, 0x5678, 0x68AC, 0),
        # Boundary case: 0x7FFF + 1 = 0x8000 (no overflow)
        (0x7FFF, 0x0001, 0x8000, 0),
        # Low byte overflow: 0x00FF + 0x0001 = 0x0100 (carry to high byte)
        (0x00FF, 0x0001, 0x0100, 0),
        # High byte overflow: 0x8000 + 0x8000 = 0x0000 (with carry)
        (0x8000, 0x8000, 0x0000, 1),
        # Maximum overflow: 0xFFFF + 1 = 0x0000 (with carry)
        (0xFFFF, 0x0001, 0x0000, 1),
        # Maximum overflow: 0xFFFF + 0xFFFF = 0xFFFE (with carry)
        (0xFFFF, 0xFFFF, 0xFFFE, 1),
    ]
    SV_all_auto_wires = (
        "  logic        _hi_adder_cin;\n"
        "  // Variables for output ports\n"
        "  logic [15:0] __sum_bits;\n"
        "  logic        __cout_bits;\n"
        "\n"
        "  // s.lo_adder = Add8()\n"
        "  logic [7:0]  _lo_adder_a;\n"
        "  logic [7:0]  _lo_adder_b;\n"
        "  logic        _lo_adder_cin;\n"
        "  Add8 lo_adder (\n"
        "    .a    (_lo_adder_a),\n"
        "    .b    (_lo_adder_b),\n"
        "    .cin  (_lo_adder_cin),\n"
        "    .sum  (__sum_bits[32'h0 +: 8]),\n"
        "    .cout (_hi_adder_cin)\n"
        "  );\n"
        "\n"
        "  // s.hi_adder = Add8()\n"
        "  logic [7:0]  _hi_adder_a;\n"
        "  logic [7:0]  _hi_adder_b;\n"
        "  Add8 hi_adder (\n"
        "    .a    (_hi_adder_a),\n"
        "    .b    (_hi_adder_b),\n"
        "    .cin  (_hi_adder_cin),\n"
        "    .sum  (__sum_bits[32'h8 +: 8]),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  assign _lo_adder_a = in1[7:0];\n"
        "  assign _lo_adder_b = in2[7:0];\n"
        "  assign _lo_adder_cin = 1'h0;\n"
        "  // s.sum[:8] @= s.lo_adder.sum\n"
        "  assign _hi_adder_a = in1[15:8];\n"
        "  assign _hi_adder_b = in2[15:8];\n"
        "  // s.sum[8:] @= s.hi_adder.sum\n"
    )

    def test_all_auto_wires(self):
        self.simulate(self.AllAutoWires(), self.TV_add16)
        self.translate(self.AllAutoWires(), self.SV_all_auto_wires)

    class PartialAutoWires(ModuleAutoWires):
        @build
        def build_all(s):
            s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0)
            s.hi_adder = Add8(cin=s.lo_adder.cout, cout=s.cout)

            s.hi_adder.a @= s.in1[8:]
            s.hi_adder.b @= s.in2[8:]
            s.sum @= cat(s.hi_adder.sum, s.lo_adder.sum)

    SV_partial_auto_wires = (
        "  wire  [7:0]  _hi_adder_sum;\n"
        "  wire  [7:0]  _lo_adder_sum;\n"
        "  wire         _lo_adder_cout;\n"
        "  // Variables for output ports\n"
        "  logic [15:0] __sum_bits;\n"
        "  logic        __cout_bits;\n"
        "\n"
        "  // s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0)\n"
        "  Add8 lo_adder (\n"
        "    .a    (in1[7:0]),\n"
        "    .b    (in2[7:0]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (_lo_adder_sum),\n"
        "    .cout (_lo_adder_cout)\n"
        "  );\n"
        "\n"
        "  // s.hi_adder = Add8(cin=s.lo_adder.cout, cout=s.cout)\n"
        "  logic [7:0]  _hi_adder_a;\n"
        "  logic [7:0]  _hi_adder_b;\n"
        "  Add8 hi_adder (\n"
        "    .a    (_hi_adder_a),\n"
        "    .b    (_hi_adder_b),\n"
        "    .cin  (_lo_adder_cout),\n"
        "    .sum  (_hi_adder_sum),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  assign _hi_adder_a = in1[15:8];\n"
        "  assign _hi_adder_b = in2[15:8];\n"
        "  assign __sum_bits = {_hi_adder_sum, _lo_adder_sum};\n"
    )

    def test_partial_auto_wires(self):
        self.simulate(self.PartialAutoWires(), self.TV_add16)
        self.translate(self.PartialAutoWires(), self.SV_partial_auto_wires)

    class ConnectOutPort(ModuleAutoWires):
        @build
        def build_all(s):
            s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0)
            s.hi_adder = Add8(s.in1[8:], s.in2[8:], s.lo_adder.cout)
            s.sum @= cat(s.hi_adder.sum, s.lo_adder.sum)
            s.cout @= s.hi_adder.cout

    SV_connect_out_port = (
        "  logic        __cout_bits;\n"
        "\n"
        "  // s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0)\n"
        "  Add8 lo_adder (\n"
        "    .a    (in1[7:0]),\n"
        "    .b    (in2[7:0]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (_lo_adder_sum),\n"
        "    .cout (_lo_adder_cout)\n"
        "  );\n"
        "\n"
        "  // s.hi_adder = Add8(s.in1[8:], s.in2[8:], s.lo_adder.cout)\n"
        "  Add8 hi_adder (\n"
        "    .a    (in1[15:8]),\n"
        "    .b    (in2[15:8]),\n"
        "    .cin  (_lo_adder_cout),\n"
        "    .sum  (_hi_adder_sum),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  assign __sum_bits = {_hi_adder_sum, _lo_adder_sum};\n"
    )

    def test_connect_out_port(self):
        self.simulate(self.ConnectOutPort(), self.TV_add16)
        self.translate(self.ConnectOutPort(), self.SV_connect_out_port)

    class ConnectInPort(ModuleAutoWires):
        @build
        def build_all(s):
            s.hi_adder = Add8(s.in1[8:], s.in2[8:])
            s.lo_adder = Add8(
                s.in1[:8], s.in2[:8], 0, s.sum[:8], s.hi_adder.cin
            )
            s.sum[8:] @= s.hi_adder.sum
            s.cout @= s.hi_adder.cout

    SV_connect_in_port = (
        "  logic        __cout_bits;\n"
        "\n"
        "  // s.hi_adder = Add8(s.in1[8:], s.in2[8:])\n"
        "  logic        _hi_adder_cin;\n"
        "  Add8 hi_adder (\n"
        "    .a    (in1[15:8]),\n"
        "    .b    (in2[15:8]),\n"
        "    .cin  (_hi_adder_cin),\n"
        "    .sum  (__sum_bits[32'h8 +: 8]),\n"
        "    .cout (__cout_bits)\n"
        "  );\n"
        "\n"
        "  // s.lo_adder = Add8(\n"
        "  Add8 lo_adder (\n"
        "    .a    (in1[7:0]),\n"
        "    .b    (in2[7:0]),\n"
        "    .cin  (1'h0),\n"
        "    .sum  (__sum_bits[32'h0 +: 8]),\n"
        "    .cout (_hi_adder_cin)\n"
        "  );\n"
    )

    def test_connect_in_port(self):
        self.simulate(self.ConnectInPort(), self.TV_add16)
        self.translate(self.ConnectInPort(), self.SV_connect_in_port)

    class OutPortSubscript(ModuleAutoWires):
        @build
        def build_all(s):
            s.lo_adder = Add8(s.in1[:8], s.in2[:8], 0)
            s.hi_adder = Add8(s.in1[8:], s.in2[8:], s.lo_adder.cout)
            s.cout @= s.hi_adder.cout
            s.sum[:7] @= s.lo_adder.sum[:7]
            s.sum[7] @= s.lo_adder.sum[7]
            s.sum[8, 7] @= s.hi_adder.sum[0, 7]
            s.sum[15] @= s.hi_adder.sum[7:]

    SV_out_port_subscript = (
        "  // s.sum[:7] @= s.lo_adder.sum[:7]\n"
        "  assign __sum_bits[32'h0 +: 7] = _lo_adder_sum[6:0];\n"
        "  // s.sum[7] @= s.lo_adder.sum[7]\n"
        "  assign __sum_bits[32'h7 +: 1] = _lo_adder_sum[7];\n"
        "  // s.sum[8, 7] @= s.hi_adder.sum[0, 7]\n"
        "  assign __sum_bits[32'h8 +: 7] = _hi_adder_sum[32'h0 +: 7];\n"
        "  // s.sum[15] @= s.hi_adder.sum[7:]\n"
        "  assign __sum_bits[32'hF +: 1] = _hi_adder_sum[7];\n"
    )

    def test_out_port_subscript(self):
        self.simulate(self.OutPortSubscript(), self.TV_add16)
        self.translate(self.OutPortSubscript(), self.SV_out_port_subscript)
