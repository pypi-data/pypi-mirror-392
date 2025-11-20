# Tests for ObjectParser
#

import pytest

import comopy.hdl as HDL
from comopy.bits import *
from comopy.ir.circt_ir import ir_to_str, ir_type_name
from comopy.ir.generate_ir import GenerateIR
from comopy.ir.structure_pass import StructurePass
from comopy.utils import match_lines


def test_ObjectParser_leaf_node():
    class Buffer(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(8)
            s.y = HDL.Output(8)
            s.y @= s.a

    class Inverter(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.din = HDL.Input(8)
            s.dout = HDL.Output(8)
            s.dout @= ~s.din

    class Top(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.tmp1 = HDL.Logic(8)
            s.tmp2 = HDL.Logic(8)
            s.tmp3 = HDL.Logic(8)
            s.tmp1 @= ~s.in_
            s.buf = Buffer(a=s.tmp1)  # read sv.LogicOp
            s.tmp2 @= s.buf.y
            s.inv = Inverter(din=s.tmp2, dout=s.tmp3)  # write sv.LogicOp
            s.out @= s.tmp3

    # No IR for @= operators, which are processed in BehaviorPass
    mlir_top = (
        "  hw.module @Top(in %in_ : i8, out out : i8) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i8>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        "    %tmp1 = sv.logic : !hw.inout<i8>\n"
        "    %tmp2 = sv.logic : !hw.inout<i8>\n"
        "    %tmp3 = sv.logic : !hw.inout<i8>\n"
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %tmp1 : !hw.inout<i8>\n"
        '    %buf.y = hw.instance "buf" @Buffer(a: %0: i8) -> (y: i8)\n'
        '    sv.verbatim ""\n'
        "    %1 = sv.read_inout %tmp2 : !hw.inout<i8>\n"
        '    %inv.dout = hw.instance "inv" @Inverter(din: %1: i8) -> '
        "(dout: i8)\n"
        "    sv.assign %tmp3, %inv.dout : i8\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim ""\n'
        "    %2 = sv.read_inout %__out_bits : !hw.inout<i8>\n"
        "    hw.output %2 : i8\n"
        "  }"
    )

    top = Top()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_top)


def test_ObjectParser_submodule_port():
    class Buffer(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(8)
            s.y = HDL.Output(8)
            s.y @= s.a

    class Inverter(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.din = HDL.Input(8)
            s.dout = HDL.Output(8)
            s.dout @= ~s.din

    class Top(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.buf = Buffer(a=s.in_)
            s.inv = Inverter(din=s.buf.y, dout=s.out)  # read instance out

    mlir_top = (
        "  hw.module @Top(in %in_ : i8, out out : i8) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i8>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        '    sv.verbatim ""\n'
        '    %buf.y = hw.instance "buf" @Buffer(a: %in_: i8) -> (y: i8)\n'
        '    sv.verbatim ""\n'
        '    %inv.dout = hw.instance "inv" @Inverter(din: %buf.y: i8) -> '
        "(dout: i8)\n"
        "    sv.assign %__out_bits, %inv.dout : i8\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim ""\n'
        "    %0 = sv.read_inout %__out_bits : !hw.inout<i8>\n"
        "    hw.output %0 : i8\n"
        "  }\n"
    )

    top = Top()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_top)


def test_ObjectParser_signal_slice():
    class Proc4(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.data = HDL.Input(4)
            s.result = HDL.Output(4)
            s.result @= s.data

    class Proc1(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.bit = HDL.Input()
            s.out = HDL.Output()
            s.out @= s.bit

    class Top(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(9)
            s.proc_low = Proc4(data=s.in_[:4], result=s.out[:4])
            s.proc_high = Proc4(data=s.in_[4:], result=s.out[4:8])
            s.proc_bit = Proc1(s.in_[0], s.out[8])

    mlir_top = (
        "  hw.module @Top(in %in_ : i8, out out : i9) {\n"
        '    sv.verbatim "// Variables for output ports"\n'
        "    %__out_bits = sv.logic : !hw.inout<i9>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// Local parameters"\n'
        '    sv.verbatim "// [MARKER] Local parameters"\n'
        '    sv.verbatim ""\n'
        "    %0 = comb.extract %in_ from 0 : (i8) -> i4\n"
        '    %proc_low.result = hw.instance "proc_low" @Proc4(data: %0: i4) '
        "-> (result: i4)\n"
        "    %c0_i32 = hw.constant 0 : i32\n"
        "    %1 = sv.indexed_part_select_inout %__out_bits[%c0_i32 : 4] "
        ": !hw.inout<i9>, i32\n"
        "    sv.assign %1, %proc_low.result : i4\n"
        '    sv.verbatim ""\n'
        "    %2 = comb.extract %in_ from 4 : (i8) -> i4\n"
        '    %proc_high.result = hw.instance "proc_high" '
        "@Proc4(data: %2: i4) -> (result: i4)\n"
        "    %c4_i32 = hw.constant 4 : i32\n"
        "    %3 = sv.indexed_part_select_inout %__out_bits[%c4_i32 : 4] "
        ": !hw.inout<i9>, i32\n"
        "    sv.assign %3, %proc_high.result : i4\n"
        '    sv.verbatim ""\n'
        "    %4 = comb.extract %in_ from 0 : (i8) -> i1\n"
        '    %proc_bit.out = hw.instance "proc_bit" '
        "@Proc1(bit: %4: i1) -> (out: i1)\n"
        "    %c8_i32 = hw.constant 8 : i32\n"
        "    %5 = sv.indexed_part_select_inout %__out_bits[%c8_i32 : 1] "
        ": !hw.inout<i9>, i32\n"
        "    sv.assign %5, %proc_bit.out : i1\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim ""\n'
        "    %6 = sv.read_inout %__out_bits : !hw.inout<i9>\n"
        "    hw.output %6 : i9\n"
        "  }"
    )

    top = Top()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    ir_str = ir_to_str(tree_s.ir_top)
    assert match_lines(ir_str, mlir_top)


def _check_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    with pytest.raises(Exception, match=error):
        GenerateIR()(tree)


#
# Sort test cases in the order of exceptions in the source code
#


def test_ObjectParser_bits_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in_

    # Bits constant
    class BitsConst(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(b8(0xAA), s.out)

    _check_error(BitsConst(), r"Bits constant or expression is not supported")

    # Bits expression
    class BitsExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(b8(0xAA) + 1, s.out)

    _check_error(BitsExpr(), r"Bits constant or expression is not supported")

    # Signal expression
    class SignalExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in1 & s.in2, s.out)

    _check_error(SignalExpr(), r"Bits constant or expression is not supported")

    # Signal extension
    class SignalExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in1.ext(8), s.out)

    _check_error(SignalExt(), r"Bits constant or expression is not supported")


def test_ObjectParser_object_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input()
            s.out = HDL.Output()
            s.tmp = HDL.Logic()
            s.out @= s.in_

    out_sub = Sub(name="out_sub")
    HDL.AssembleHDL()(out_sub)

    out_sub_same_name = Sub(name="top")
    HDL.AssembleHDL()(out_sub_same_name)

    # Submodule instance outside current module
    class OutsideInst(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.out, out_sub.in_)

    _check_error(OutsideInst(), r"object out_sub\.in_ is not accessible")

    # Homonym module with the same name as current module
    class HomonymModule(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(out_sub_same_name.out, s.out)

    _check_error(HomonymModule(name="top"), r"top\.out is not accessible")

    # Assign to input port
    class AssignInput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.in2 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1, s.in2)

    _check_error(AssignInput(), r"Cannot assign to input port 'in2'")

    # Not a port
    class NotPort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub1 = Sub()
            s.sub2 = Sub(s.sub1.tmp, s.out)

    _check_error(NotPort(), r"object sub1\.tmp is not a port")

    # Read from submodule input port
    class ReadSubInput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.in2 = HDL.Input()
            s.out = HDL.Output()
            s.sub1 = Sub(s.in1)
            s.sub2 = Sub(s.sub1.in_)
            s.out @= s.sub1.out ^ s.sub2.out

    _check_error(ReadSubInput(), r"Cannot read .* input port sub1\.in_")


def test_ObjectParser_slice_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in_

    # Bits as lower bound
    class BitsLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[b8(0) :], s.out)

    _check_error(BitsLower(), r"Lower bound must be an integer")

    # Vector as lower bound
    class VectorLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[s.idx :], s.out)

    _check_error(VectorLower(), r"Lower bound must be an integer")

    # Bits as upper bound
    class BitsUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_, s.out[: b8(8)])

    _check_error(BitsUpper(), r"Upper bound must be an integer")

    # Vector as upper bound
    class VectorUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_, s.out[: s.idx + b8(8)])

    _check_error(VectorUpper(), r"Upper bound must be an integer")


def test_ObjectParser_part_select_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in_

    # Bits as base
    class BitsBase(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[b8(0), 8], s.out)

    _check_error(BitsBase(), r"Part-select base must be an integer")

    # Vector as base
    class VectorBase(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[s.idx, 8], s.out)

    _check_error(VectorBase(), r"Part-select base must be an integer")

    # Bits as width
    class BitsWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_, s.out[0, b8(8)])

    _check_error(BitsWidth(), r"Part-select width must be an integer")

    # Vector as width
    class VectorWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_, s.out[0, s.idx + b8(8)])

    _check_error(VectorWidth(), r"Part-select width must be an integer")


def test_ObjectParser_index_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input()
            s.out = HDL.Output()
            s.out @= s.in_

    # Bits as index
    class BitsIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[b8(0)], s.out[0])

    _check_error(BitsIndex(), r"Index must be an integer constant")

    # Vector as index
    class VectorIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[s.idx], s.out[0])

    _check_error(VectorIndex(), r"Index must be an integer constant")

    # Vector expression as index
    class ExprIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in_[0], s.out[s.idx + 1])

    _check_error(ExprIndex(), r"Index must be an integer constant")


# Print all error messages by replacing _check_error
#
def _print_parsing_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    try:
        GenerateIR()(tree)
    except Exception as e:
        print(e)


def print_ObjectParser_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_parsing_error
    test_ObjectParser_bits_errors()
    test_ObjectParser_object_errors()
    test_ObjectParser_slice_errors()
    test_ObjectParser_part_select_errors()
    test_ObjectParser_index_errors()
    _check_error = orig_check_error
