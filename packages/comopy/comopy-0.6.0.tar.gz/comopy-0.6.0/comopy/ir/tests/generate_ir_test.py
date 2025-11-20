# Tests for GenerateIR
#

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy.hdl import HDLStage
from comopy.ir.circt_ir import *
from comopy.ir.generate_ir import GenerateIR
from comopy.utils import match_lines


def test_GenerateIR_call():
    mlir_module = (
        "module {\n"
        "  hw.module @Wire1(in %in_ : i1, out out : i1) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// @comb update():"\n'
        "    sv.alwayscomb {\n"
        "      sv.bpassign %__out_bits, %in_ : i1\n"
        "    }\n"
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %__out_bits : !hw.inout<i1>\n"
        "    hw.output %0 : i1\n"
        "  }\n"
        "}\n"
    )

    top = ex.Wire1()
    tree = HDLStage()(top)
    tree_ir = GenerateIR()(tree)
    assert tree_ir is tree
    assert ir_type_name(tree_ir.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_ir.ir_top)
    assert match_lines(ir_str, mlir_module)
