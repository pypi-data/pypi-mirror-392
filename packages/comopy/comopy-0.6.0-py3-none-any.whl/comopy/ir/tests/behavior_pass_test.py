# Tests for BehaviorPass
#

import comopy.hdl as HDL
import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy.ir.behavior_pass import BehaviorPass
from comopy.ir.circt_ir import ir_to_str, ir_type_name
from comopy.ir.structure_pass import StructurePass
from comopy.utils import match_lines


def test_BehaviorPass_call():
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
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    assert tree_s is tree
    assert ir_type_name(tree_s.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    tree_b = BehaviorPass()(tree_s)
    assert tree_b is tree_s
    assert ir_type_name(tree_b.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    bir_str = ir_to_str(tree_b.ir_top)
    assert match_lines(bir_str, mlir_module)


def test_BehaviorPass_no_outport():
    class Tester(HDL.RawModule):
        @HDL.build
        def no_ports(s):
            s.a = HDL.Logic()
            s.b = HDL.Logic()
            s.c = HDL.Logic()

        @HDL.comb
        def update(s):
            s.a /= 1
            s.b /= 0
            s.c /= s.a & s.b

    mlir_module = (
        "module {\n"
        "  hw.module @Tester() {\n"
        "    %a = sv.logic : !hw.inout<i1>\n"
        "    %b = sv.logic : !hw.inout<i1>\n"
        "    %c = sv.logic : !hw.inout<i1>\n"
        '    sv.verbatim ""\n'
        '    sv.verbatim "// @comb update():"\n'
        "    sv.alwayscomb {\n"
        "      %true = hw.constant true\n"
        "      sv.bpassign %a, %true : i1\n"
        "      %false = hw.constant false\n"
        "      sv.bpassign %b, %false : i1\n"
        "      %0 = sv.read_inout %a : !hw.inout<i1>\n"
        "      %1 = sv.read_inout %b : !hw.inout<i1>\n"
        "      %2 = comb.and %0, %1 : i1\n"
        "      sv.bpassign %c, %2 : i1\n"
        "    }\n"
        '    sv.verbatim ""\n'
        "    hw.output\n"
        "  }\n"
        "}\n"
    )

    top = Tester()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    tree_b = BehaviorPass()(tree_s)
    assert ir_type_name(tree_b.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    bir_str = ir_to_str(tree_b.ir_top)
    assert match_lines(bir_str, mlir_module)


def test_BehaviorPass_copy_from_template():
    class Inner(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= ~s.in_

    class Sub(HDL.Module):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.inner = Inner(s.in_)
            s.reg = HDL.Logic(8)
            s.result = HDL.Logic(8)
            s.out @= s.result

        @HDL.seq
        def update_ff(s):
            s.reg <<= s.inner.out + 1

        @HDL.comb
        def update(s):
            s.result /= s.reg + 2

    class Top(HDL.Module):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.u1 = Sub(s.in1)
            s.u2 = Sub(s.in2)
            s.out @= s.u1.out + s.u2.out

    top = Top()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    tree_b = BehaviorPass()(tree_s)
    assert tree_b is tree_s
    assert ir_type_name(tree_b.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    assert ir_type_name(top.u1.ir) == "HWModuleOp"
    assert top.u2.ir is None

    node = top.u2.node
    assert len(node.inst_blocks) == 1
    assert not node.inst_blocks[0].edges.pos_edges
    assert not node.inst_blocks[0].edges.neg_edges
    assert node.inst_blocks[0].deps.reads == {"inner.in_"}
    assert node.inst_blocks[0].deps.writes == {"inner.out"}
    assert node.inst_blocks[0].id == "[inst]inner"
    assert len(node.conn_blocks) == 2
    assert not node.conn_blocks[0].edges.pos_edges
    assert not node.conn_blocks[0].edges.neg_edges
    assert node.conn_blocks[0].deps.reads == {"in_"}
    assert node.conn_blocks[0].deps.writes == {"inner.in_"}
    assert node.conn_blocks[0].id == "[conn]inner.in_"
    assert not node.conn_blocks[1].edges.pos_edges
    assert not node.conn_blocks[1].edges.neg_edges
    assert node.conn_blocks[1].deps.reads == {"result"}
    assert node.conn_blocks[1].deps.writes == {"out"}
    assert node.conn_blocks[1].id == "[conn]s.out"
    assert len(node.comb_blocks) == 1
    assert not node.comb_blocks[0].edges.pos_edges
    assert not node.comb_blocks[0].edges.neg_edges
    assert node.comb_blocks[0].deps.reads == {"reg"}
    assert node.comb_blocks[0].deps.writes == {"result"}
    assert node.comb_blocks[0].id == "[comb]update"
    assert len(node.seq_blocks) == 1
    assert node.seq_blocks[0].edges.pos_edges == ["clk"]
    assert not node.seq_blocks[0].edges.neg_edges
    assert node.seq_blocks[0].deps.reads == {"clk", "inner.out"}
    assert node.seq_blocks[0].deps.writes == {"reg"}
    assert node.seq_blocks[0].id == "[seq]update_ff"
