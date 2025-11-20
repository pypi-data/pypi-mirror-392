# Tests for StructurePass
#

import pytest

import comopy.hdl as HDL
import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy.ir.circt_ir import ir_to_str, ir_type_name
from comopy.ir.structure_pass import StructurePass
from comopy.utils import match_lines


def test_StructurePass_call():
    mlir_module = (
        "module {\n"
        "  hw.module @Wire1(in %in_ : i1, out out : i1) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %__out_bits : !hw.inout<i1>\n"
        "    hw.output %0 : i1\n"
        "  }\n"
        "}\n"
    )

    top = ex.Wire1(name="top")
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert tree_s is tree
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_module)

    with pytest.raises(RuntimeError, match=r"IR has already .* Wire1\(top\)"):
        StructurePass()(tree_s)


def test_StructurePass_no_outport():
    class Tester(HDL.RawModule):
        @HDL.build
        def no_ports(s):
            s.a = HDL.Logic()
            s.b = HDL.Logic()
            s.c = HDL.Logic()

        @HDL.comb
        def update(s):
            s.c /= s.a & s.b

    mlir_module = (
        "module {\n"
        "  hw.module @Tester() {\n"
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        "    %a = sv.logic : !hw.inout<i1>\n"
        "    %b = sv.logic : !hw.inout<i1>\n"
        "    %c = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        "    hw.output\n"
        "  }\n"
        "}\n"
    )

    top = Tester()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert tree_s is tree
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_module)


def test_StructurePass_submodule():
    class NoInOut(HDL.RawModule):
        @HDL.build
        def build_all(s):
            ...

    class Sub1(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.x = HDL.Input()
            s.out = HDL.Output()
            s.out @= s.x

    class Sub2(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input()
            s.b = HDL.Input()
            s.out = HDL.Output()
            s.out @= s.a ^ s.b

    class Top(HDL.RawModule):
        @HDL.build
        def ports(s):
            s.in1 = HDL.Input()
            s.in2 = HDL.Input()
            s.in3 = HDL.Input()
            s.in4 = HDL.Input()
            s.out = HDL.Output()
            s.res1 = HDL.Logic()
            s.res2 = HDL.Logic()
            s.res3 = HDL.Logic()
            s.out @= s.res1 & s.res2 & s.res3

        @HDL.build
        def build_no_inout_sub(s):
            s.no_inout = NoInOut()

        @HDL.build
        def build_inout_sub(s):
            s.sub1 = Sub1(s.in1, s.res1)
            s.sub2 = Sub2(a=s.in2, b=s.in3, out=s.res2)
            s.sub3 = Sub1(s.in4, s.res3)

    mlir_top = (
        "  hw.module @Top(in %in1 : i1, in %in2 : i1, in %in3 : i1, "
        "in %in4 : i1, out out : i1) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        "    %res1 = sv.logic : !hw.inout<i1>\n"
        "    %res2 = sv.logic : !hw.inout<i1>\n"
        "    %res3 = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        '    hw.instance "no_inout" @NoInOut() -> ()\n'
        '    sv.verbatim ""\n'
        '    %sub1.out = hw.instance "sub1" @Sub1(x: %in1: i1) -> (out: i1)\n'
        "    sv.assign %res1, %sub1.out : i1\n"
        '    sv.verbatim ""\n'
        '    %sub2.out = hw.instance "sub2" @Sub2(a: %in2: i1, b: %in3: i1) '
        "-> (out: i1)\n"
        "    sv.assign %res2, %sub2.out : i1\n"
        '    sv.verbatim ""\n'
        '    %sub3.out = hw.instance "sub3" @Sub1(x: %in4: i1) -> (out: i1)\n'
        "    sv.assign %res3, %sub3.out : i1\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %__out_bits : !hw.inout<i1>\n"
        "    hw.output %0 : i1\n"
        "  }\n"
    )

    top = Top()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert tree_s is tree
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    assert ir_type_name(top.no_inout.ir) == "HWModuleOp"
    assert ir_type_name(top.sub1.ir) == "HWModuleOp"
    assert ir_type_name(top.sub2.ir) == "HWModuleOp"
    assert top.sub3.ir is None
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_top)


def _check_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    with pytest.raises(Exception, match=error):
        StructurePass()(tree)


def test_StructurePass_array():
    class Memory(HDL.Module):
        @HDL.build
        def build_all(s):
            s.addr = HDL.Input(4)
            s.data = HDL.Output(8)

            s.mem = HDL.Logic(8) @ 16
            s.data @= s.mem[s.addr]

    mlir_module = (
        "module {\n"
        "  hw.module @Memory(in %clk : i1, in %addr : i4, out data : i8) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__data_bits = sv.logic : !hw.inout<i8>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        "    %mem = sv.logic : !hw.inout<uarray<16xi8>>\n"
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %__data_bits : !hw.inout<i8>\n"
        "    hw.output %0 : i8\n"
        "  }\n"
        "}\n"
    )

    top = Memory()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert tree_s is tree
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_module)


#
# Sort test cases in the order of exceptions in the source code
#


def test_StructurePass_generate_errors():
    from comopy.hdl import CircuitObject

    # Unsupported HDL type
    class Unsupported(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = CircuitObject()

    _check_error(Unsupported(), r"Unsupported .* 'CircuitObject'")


# Print all error messages by replacing _check_error
#
def _print_structure_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    try:
        StructurePass()(tree)
    except Exception as e:
        print(e)


def print_StructurePass_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_structure_error
    test_StructurePass_generate_errors()
    _check_error = orig_check_error
