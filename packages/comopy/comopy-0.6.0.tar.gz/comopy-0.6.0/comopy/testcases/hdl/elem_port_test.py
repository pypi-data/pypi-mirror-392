# Tests for HDL structural element: port
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


class TestScalarPorts(BaseTestCase):
    class ScalarPorts(RawModule):
        @build
        def ports(s):
            s.valid = Input()
            s.ack = Output()
            s.out = Output()

        @comb
        def update(s):
            s.ack /= s.valid
            s.out /= s.valid

    class IO(IOStruct):
        valid = Input()
        ack = Output()
        out = Output()

    TV = [IO(), (0, 0, 0), (1, 1, 1)]

    SV = (
        "  input  wire valid,\n"
        "  output wire ack,\n"
        "              out\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic __ack_bits;\n"
        "  logic __out_bits;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __ack_bits = valid;\n"
        "    __out_bits = valid;\n"
        "  end // always_comb\n"
        "\n"
        "  assign ack = __ack_bits;\n"
        "  assign out = __out_bits;\n"
        "endmodule\n"
    )

    def test_scalar_ports(self):
        self.simulate(self.ScalarPorts(), self.TV)
        self.translate(self.ScalarPorts(), self.SV)


class TestVectorPorts(BaseTestCase):
    class VectorPorts(RawModule):
        @build
        def ports(s):
            s.a = Input(4)
            s.b = Input(4)
            s.and_out = Output(4)
            s.or_out = Output(4)
            s.xnor_out = Output(4)

        @comb
        def update(s):
            s.and_out /= s.a & s.b
            s.or_out /= s.a | s.b
            s.xnor_out /= ~(s.a ^ s.b)

    class IO(IOStruct):
        a = Input(4)
        b = Input(4)
        and_out = Output(4)
        or_out = Output(4)
        xnor_out = Output(4)

    TV = [
        IO(),
        (0b0000, 0b0000, 0b0000, 0b0000, 0b1111),
        (0b0101, 0b0011, 0b0001, 0b0111, 0b1001),
        (0b1111, 0b0000, 0b0000, 0b1111, 0b0000),
        (0b1100, 0b1010, 0b1000, 0b1110, 0b1001),
    ]

    SV = (
        "  input  wire [3:0] a,\n"
        "                    b,\n"
        "  output wire [3:0] and_out,\n"
        "                    or_out,\n"
        "                    xnor_out\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic [3:0] __and_out_bits;\n"
        "  logic [3:0] __or_out_bits;\n"
        "  logic [3:0] __xnor_out_bits;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __and_out_bits = a & b;\n"
        "    __or_out_bits = a | b;\n"
        "    __xnor_out_bits = ~(a ^ b);\n"
        "  end // always_comb\n"
        "\n"
        "  assign and_out = __and_out_bits;\n"
        "  assign or_out = __or_out_bits;\n"
        "  assign xnor_out = __xnor_out_bits;\n"
        "endmodule\n"
    )

    def test_vector_ports(self):
        self.simulate(self.VectorPorts(), self.TV)
        self.translate(self.VectorPorts(), self.SV)


class TestPortOrder(BaseTestCase):
    class MixedInOut(RawModule):
        @build
        def ports(s):
            s.in_scalar = Input()
            s.out_scalar = Output()
            s.in_vector = Input(4)
            s.out_vector = Output(4)
            s.out_scalar @= 0
            s.out_vector @= 0

    SV = (
        "  input  wire       in_scalar,\n"
        "  output wire       out_scalar,\n"
        "  input  wire [3:0] in_vector,\n"
        "  output wire [3:0] out_vector\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic       __out_scalar_bits;\n"
        "  logic [3:0] __out_vector_bits;\n"
        "\n"
        "  assign __out_scalar_bits = 1'h0;\n"
        "  assign __out_vector_bits = 4'h0;\n"
        "\n"
        "  assign out_scalar = __out_scalar_bits;\n"
        "  assign out_vector = __out_vector_bits;\n"
        "endmodule\n"
    )

    def test_port_order(self):
        self.translate(self.MixedInOut(), self.SV)
