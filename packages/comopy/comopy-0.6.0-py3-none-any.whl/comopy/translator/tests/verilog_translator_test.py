# Tests for VerilogTranslator
#

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage, IRStage, JobPipeline
from comopy.ir.circt_ir import ir_to_raw_str, ir_to_str
from comopy.translator.verilog_translator import VerilogTranslator


def test_VerilogTranslator_emit():
    sv_top = (
        "module Wire1(\n"
        "  input  wire in_,\n"
        "  output wire out\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic __out_bits;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in_;\n"
        "\n"
        "  assign out = __out_bits;\n"
        "endmodule"
    )

    top = ex.Wire1()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    trans = VerilogTranslator(tree_ir)

    sv = trans.emit()
    assert sv == sv_top


def test_VerilogTranslator_debug(project_path):
    module = ex.Wire1()
    pipeline = JobPipeline(HDLStage(), IRStage())
    tree_ir = pipeline(module)
    sv = VerilogTranslator(tree_ir).emit()

    filename = f"{project_path}/comopy/tests_out/TranslateVerilog_test"
    with open(f"{filename}.mlir", "w") as f:
        f.write(ir_to_str(tree_ir.ir_top))

    with open(f"{filename}.raw.mlir", "w") as f:
        f.write(ir_to_raw_str(tree_ir.ir_top))

    with open(f"{filename}.sv", "w") as f:
        f.write(sv)
        f.write("\n")
