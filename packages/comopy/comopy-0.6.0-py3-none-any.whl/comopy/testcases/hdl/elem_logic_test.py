# Tests for HDL structural element: logic
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    Logic,
    Output,
    RawModule,
    build,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestLogicDecl(BaseTestCase):
    class LogicDecl(RawModule):
        @build
        def ports(s):
            s.a = Input(4)
            s.b = Input(4)
            s.result = Output(4)
            s.result @= 0

        @build
        def decl(s):
            s.or_val = Logic(4)
            s.and_val = Logic(4)
            s.odd = Logic()

    SV = (
        "module LogicDecl(\n"
        "  input  wire [3:0] a,\n"
        "                    b,\n"
        "  output wire [3:0] result\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic [3:0] __result_bits;\n"
        "\n"
        "  logic [3:0] or_val;\n"
        "  logic [3:0] and_val;\n"
        "  logic       odd;\n"
    )

    def test_logic_decl(self):
        self.translate(self.LogicDecl(), self.SV)
