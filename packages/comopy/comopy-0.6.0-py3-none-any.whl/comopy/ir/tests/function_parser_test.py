# Tests for FunctionParser
#

import pytest

import comopy.hdl as HDL
from comopy import Bits, Bool, cat, rep
from comopy.bits import *
from comopy.bits import b2, b3, b4, b8  # type: ignore
from comopy.ir.behavior_pass import BehaviorPass
from comopy.ir.circt_ir import ir_to_str, ir_type_name
from comopy.ir.structure_pass import StructurePass
from comopy.utils import HDLSyntaxError, match_lines


def test_FunctionParser_conn_deps():
    class ConnDeps(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.in3 = HDL.Input(4)
            # s.out1 = out1 = HDL.Output(8)
            s.out1 = HDL.Output(8)
            s.out2 = HDL.Output(8)
            s.out3 = HDL.Output(4)
            s.logic1 = HDL.Logic(8)
            s.logic2 = HDL.Logic(4)
            s.logic3 = HDL.Logic(8)

            s.out1 @= ~s.logic1  # TODO local variable
            s.logic2 @= s.in2 ^ s.in3  # expression
            s.logic1[:4] @= s.in2 if s.in1 > 5 else s.in3  # conditional expr
            s.logic1[4:] @= s.logic1[:4]
            s.logic3 @= cat(s.in1[2:6], s.in2[:2], b2(3))  # read slice, const
            s.out2[:4] @= s.logic2  # write slice
            s.out2[4:] @= rep(4, s.logic3[7])  # read overlapped bundle
            cat(s.out3[:2], s.out3[2])[:] @= s.logic3[2:5]  # no overlap
            s.out3[3] @= 0  # to avoid incomplete driving

    top = ConnDeps()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    BehaviorPass()(tree_s)
    conns = tree.conn_blocks
    assert len(conns) == 9
    deps = conns[0].deps
    assert deps.reads == {"logic1"}
    assert deps.writes == {"out1"}
    deps = conns[1].deps
    assert deps.reads == {"in2", "in3"}
    assert deps.writes == {"logic2"}
    deps = conns[2].deps
    assert deps.reads == {"in1", "in2", "in3"}
    assert deps.writes == {"logic1"}
    deps = conns[3].deps
    assert deps.reads == {"logic1"}
    assert deps.writes == {"logic1"}
    deps = conns[4].deps
    assert deps.reads == {"in1", "in2"}
    assert deps.writes == {"logic3"}
    deps = conns[5].deps
    assert deps.reads == {"logic2"}
    assert deps.writes == {"out2"}
    deps = conns[6].deps
    assert deps.reads == {"logic3"}
    assert deps.writes == {"out2"}
    deps = conns[7].deps
    assert deps.reads == {"logic3"}
    assert deps.writes == {"out3"}
    deps = conns[8].deps
    assert deps.reads == set()
    assert deps.writes == {"out3"}


def test_FunctionParser_comb_deps():
    class CombDeps(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.in3 = HDL.Input(4)
            s.idx = HDL.Input(3)
            s.out1 = HDL.Output(8)
            s.out2 = HDL.Output(8)
            s.out3 = HDL.Output(4)
            s.logic1 = HDL.Logic(8)
            s.logic2 = HDL.Logic(4)
            s.logic3 = HDL.Logic(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.logic1 /= cat(s.in2, s.in3)  # concatenation
            s.logic2 /= s.in2 ^ s.in3  # expression
            s.logic3 /= cat(s.in1[2:6], s.in2[:2], b2(3))  # read slice, const
            s.out1 /= 0
            s.out1[s.idx] /= ~s.logic1[0]  # read at LHS
            s.out2[:4] /= s.logic2  # write slice
            s.out2[4:] /= rep(4, s.logic3[7])  # read overlapped bundle
            cat(s.out3[:2], s.out3[2])[:] /= s.logic3[2:5]  # no overlap

    top = CombDeps()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    BehaviorPass()(tree_s)
    blocks = tree.comb_blocks
    assert blocks[0].func.__name__ == "update"
    deps = blocks[0].deps
    assert deps.reads == {"in1", "in2", "in3", "idx"}
    assert deps.writes == {
        "out1",
        "out2",
        "out3",
        "logic1",
        "logic2",
        "logic3",
    }


def test_FunctionParser_if_deps():
    class IfDeps(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.sel = HDL.Input()
            s.out1 = HDL.Output(8)
            s.out2 = HDL.Output(4)
            s.logic1 = HDL.Logic(8)
            s.logic2 = HDL.Logic(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            if s.sel:
                s.logic1 /= s.in1
                s.out1 /= s.logic1
            else:
                s.logic2 /= s.in2
                s.out2 /= s.logic2

    top = IfDeps()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    BehaviorPass()(tree_s)
    blocks = tree.comb_blocks
    assert blocks[0].func.__name__ == "update"
    deps = blocks[0].deps
    assert deps.reads == {"in1", "in2", "sel"}
    assert deps.writes == {"out1", "out2", "logic1", "logic2"}


def test_FunctionParser_case_deps():
    class CaseDeps(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.sel = HDL.Input(2)
            s.out1 = HDL.Output(8)
            s.out2 = HDL.Output(4)
            s.logic1 = HDL.Logic(8)
            s.logic2 = HDL.Logic(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out1 /= 0
            match s.sel:
                case 0:
                    s.logic1 /= s.in1
                    s.out1 /= s.logic1
                case 1:
                    s.logic2 /= s.in2
                    s.out2 /= s.logic2
                case 2:
                    s.logic1 /= cat(s.in2, b4(3))
                    s.out1 /= s.logic1
                case _:
                    s.logic2 /= 0
                    s.out2 /= s.logic2

    top = CaseDeps()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    BehaviorPass()(tree_s)
    blocks = tree.comb_blocks
    assert blocks[0].func.__name__ == "update"
    deps = blocks[0].deps
    assert deps.reads == {"in1", "in2", "sel"}
    assert deps.writes == {"out1", "out2", "logic1", "logic2"}


def test_FunctionParser_seq_block_edges():
    class RawTop(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.rst1 = HDL.Input()
            s.rst2 = HDL.Input()
            s.reg = HDL.Logic(8)

        @HDL.seq
        def update_seq(s, posedge="clk", negedge=("rst1", "rst2")):
            if (~s.rst1) | (~s.rst2):
                s.reg <<= 0
            else:
                s.reg <<= 42

    SV_always = "    sv.always posedge %clk, negedge %rst1, negedge %rst2 {\n"

    top = RawTop()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    tree_b = BehaviorPass()(tree_s)
    assert tree_s is tree
    assert tree_b is tree_s
    assert len(tree_b.seq_blocks) == 1
    block = tree_b.seq_blocks[0]
    assert block.edges.pos_edges == ["clk"]
    assert block.edges.neg_edges == ["rst1", "rst2"]

    assert ir_type_name(tree_b.ir_top) == "Module"
    assert ir_type_name(top.ir) == "HWModuleOp"
    bir_str = ir_to_str(tree_b.ir_top)
    assert match_lines(bir_str, SV_always)


def test_FunctionParser_seq_deps():
    class SeqDeps(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input(1)
            s.rst_n = HDL.Input(1)
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.out1 = HDL.Output(8)
            s.out2 = HDL.Output(4)
            s.reg1 = HDL.Logic(8)
            s.reg2 = HDL.Logic(4)

        @HDL.seq
        def update(s, posedge="clk", negedge="rst_n"):  # pragma: no cover
            s.reg1 <<= s.in1
            s.reg2 <<= s.in2
            s.out1 <<= s.reg1
            s.out2 <<= s.reg2

    top = SeqDeps()
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    BehaviorPass()(tree_s)
    blocks = tree.seq_blocks
    assert blocks[0].func.__name__ == "update"
    deps = blocks[0].deps
    assert deps.reads == {"clk", "rst_n", "in1", "in2"}
    assert deps.writes == {"out1", "out2", "reg1", "reg2"}
    edges = blocks[0].edges
    assert edges.pos_edges == ["clk"]
    assert edges.neg_edges == ["rst_n"]


def _check_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    tree_s = StructurePass()(tree)
    with pytest.raises(HDLSyntaxError, match=error):
        BehaviorPass()(tree_s)


#
# Sort test cases in the order of exceptions in the source code
#


def test_FunctionParser_driving_errors():
    class UndrivenOutput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

    _check_error(UndrivenOutput(), r"UndrivenOutput, .* 'out' is not driven")

    class UndrivenConn(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.temp = HDL.Logic(8)
            s.out @= s.in_ + s.temp

    _check_error(UndrivenConn(), r"build_all\(\), 'temp' is not driven")

    class UndrivenComb(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.temp = HDL.Logic(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ + s.temp

    _check_error(UndrivenComb(), r"update\(\), 'temp' is not driven")

    class UndrivenSeq(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.temp = HDL.Logic(8)

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out <<= s.in_ + s.temp

    _check_error(UndrivenSeq(), r"update_ff\(\), 'temp' is not driven")

    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.din = HDL.Input(8)
            s.en = HDL.Input()
            s.dout = HDL.Output(8)
            s.dout @= s.din

    class UndrivenInstPort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.sub = Sub(en=1, dout=s.out)

    _check_error(UndrivenInstPort(), r"sub, 'sub.din' is not driven")


def test_FunctionParser_port_connection_errors():
    # Incomplete driving in port connection
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)
            s.out @= s.in_

    class IncompleteDrive(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output(8)
            s.sub = Sub(s.in1, s.out[:4])

    _check_error(IncompleteDrive(), r"Signal 'out' is not fully driven")

    # Incomplete driving port in port connection
    class Swap(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.data = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= cat(s.data[4:], s.data[:4])

    class IncompleteDrivePort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.swap = Swap(out=s.out)
            s.sub = Sub(s.in1[:4], s.swap.data[:4])

    _check_error(IncompleteDrivePort(), r"'swap.data' is not fully driven")


def test_FunctionParser_connection_errors():
    # HDL assembler performs width and multi-drive checks.
    # Test cases not handled by the assembler.

    # Connect from boolean AND
    class ConnectBoolAnd(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in1 and s.in2

    _check_error(ConnectBoolAnd(), r"Boolean 'and' requires Bool\(\)")

    # Connect from boolean OR
    class ConnectBoolOr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in1 or s.in2

    _check_error(ConnectBoolOr(), r"Boolean 'or' requires Bool\(\)")

    # Connect from boolean OR with integer
    class ConnectBoolOrInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.out @= s.in1 or 5

    _check_error(ConnectBoolOrInt(), r"Boolean 'or' requires Bool\(\)")

    # Connect with variable index on LHS
    class ConnectVarIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.out[s.idx] @= s.in_[0]

    _check_error(ConnectVarIndex(), r"\(@=\) requires constant index")

    # Connect with variable start index in part-select on LHS
    class ConnectVarStartIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(3)
            s.out = HDL.Output(8)
            s.out[s.idx, 4] @= s.in_[:4]

    _check_error(ConnectVarStartIndex(), r"\(@=\) requires constant start")

    # Connect with expression index on LHS
    class ConnectExprIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx1 = HDL.Input(2)
            s.idx2 = HDL.Input(2)
            s.out = HDL.Output(8)
            s.out[s.idx1 + s.idx2] @= s.in_[0]

    _check_error(ConnectExprIndex(), r"\(@=\) requires constant index")

    # Connect with incomplete driving
    class IncompleteDrive(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out[:4] @= s.in_[:4]

    _check_error(IncompleteDrive(), r"not fully driven")

    # Connect with incomplete driving for cat() as LHS
    class IncompleteDriveConcat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)
            cat(s.out1[:2], s.out2)[:] @= s.in_[:6]

    _check_error(IncompleteDriveConcat(), r"not fully driven")


def test_FunctionParser_comb_block_errors():
    # No self argument
    class NoSelf(HDL.RawModule):
        @HDL.comb
        def update():  # pragma: no cover
            ...

    _check_error(NoSelf(), r"@comb block must take exactly one 'self'")

    # Bad arguments
    class VarArgs(HDL.RawModule):
        @HDL.comb
        def update(s, *args):  # pragma: no cover
            ...

    _check_error(VarArgs(), r"cannot use \*args or \*\*kwargs")

    class KwOnlyArgs(HDL.RawModule):
        @HDL.comb
        def update(s, *, a, b):  # pragma: no cover
            ...

    _check_error(KwOnlyArgs(), r"cannot use \*args or \*\*kwargs")

    # Default self argument
    class DefaultSelf(HDL.RawModule):
        @HDL.comb
        def update(self=0):  # pragma: no cover
            ...

    _check_error(DefaultSelf(), r"'self' .* cannot have a default value")


def test_FunctionParser_seq_block_errors():
    # No self argument
    class NoSelf(HDL.RawModule):
        @HDL.seq
        def update_ff():  # pragma: no cover
            ...

    _check_error(NoSelf(), r"@seq block must have a 'self' argument")

    # Too many arguments
    class TooManyArgs(HDL.RawModule):
        @HDL.seq
        def update_ff(s, a, b, c):  # pragma: no cover
            ...

    _check_error(TooManyArgs(), r"must have at most 3 arguments:")

    # Bad arguments
    class VarArgs(HDL.RawModule):
        @HDL.seq
        def update(s, *args):  # pragma: no cover
            ...

    _check_error(VarArgs(), r"cannot use \*args or \*\*kwargs")

    class KwOnlyArgs(HDL.RawModule):
        @HDL.seq
        def update(s, *, a, b):  # pragma: no cover
            ...

    _check_error(KwOnlyArgs(), r"cannot use \*args or \*\*kwargs")

    # Default self argument
    class DefaultSelf(HDL.RawModule):
        @HDL.seq
        def update(self=0):  # pragma: no cover
            ...

    _check_error(DefaultSelf(), r"'self' .* cannot have a default value")

    # Bad self argument
    class BadSelf(HDL.RawModule):
        @HDL.seq
        def update_ff(negedge):  # pragma: no cover
            ...

    _check_error(BadSelf(), r"@seq block the first argument must be 'self'")

    # No edge argument
    class NoEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s):  # pragma: no cover
            ...

    _check_error(NoEdge(), r"requires at least one edge argument")


def test_FunctionParser_seq_block_edge_errors():
    # Not edge argument
    class NotEdgeArg1(HDL.RawModule):
        @HDL.seq
        def update_ff(s, a):  # pragma: no cover
            ...

    _check_error(NotEdgeArg1(), r"should be 'posedge' or 'negedge'")

    class NotEdgeArg2(HDL.RawModule):
        @HDL.seq
        def update_ff(s, negedge="in", a=0):  # pragma: no cover
            ...

    _check_error(NotEdgeArg2(), r"should be 'posedge' or 'negedge'")

    # No value for edge argument
    class NoValueEdgeArg1(HDL.RawModule):
        @HDL.seq
        def update_ff(s, posedge):  # pragma: no cover
            ...

    _check_error(NoValueEdgeArg1(), r"'posedge' must be a signal .* tuple")

    class NoValueEdgeArg2(HDL.RawModule):
        @HDL.seq
        def update_ff(s, negedge, posedge):  # pragma: no cover
            ...

    _check_error(NoValueEdgeArg2(), r"'negedge' must be a signal .* tuple")

    # Wrong type for edge argument
    class WrongTypeEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s, negedge=["rst"]):  # pragma: no cover
            ...

    _check_error(WrongTypeEdge(), r"'negedge' must be a string or tuple")

    # Empty string for edge argument
    class EmptyStrEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s, negedge=""):  # pragma: no cover
            ...

    _check_error(EmptyStrEdge(), r"'negedge' cannot be an empty string")

    # Not string for edge argument
    class NotStrEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s, posedge=0):  # pragma: no cover
            ...

    _check_error(NotStrEdge(), r"'posedge' must be a string or tuple")

    # Auto edge conflicts
    class AutoPosEdgeConflict(HDL.RawModule):
        _auto_pos_edges = ("clk",)

        @HDL.build
        def build_all(s):
            s.data = HDL.Logic()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.data <<= 1

    _check_error(AutoPosEdgeConflict(), r"'clk' is already an automatic edge")

    class AutoNegEdgeConflict(HDL.RawModule):
        _auto_neg_edges = ("rst_n",)

        @HDL.build
        def build_all(s):
            s.data = HDL.Logic()

        @HDL.seq
        def update_ff(s, negedge="rst_n"):  # pragma: no cover
            s.data <<= 0

    _check_error(AutoNegEdgeConflict(), r"'rst_n' is already an automatic")

    # Empty tuple for edge argument
    class EmptyTupleEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s, negedge=(), posedge=()):  # pragma: no cover
            ...

    _check_error(EmptyTupleEdge(), r"'posedge' cannot be an empty tuple")

    # Not string tuple for edge argument
    class NotStrTupleEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()

        @HDL.seq
        def update_ff(s, negedge=("clk", 0)):  # pragma: no cover
            ...

    _check_error(NotStrTupleEdge(), r"'negedge' must be a string or tuple")

    class NestedTupleEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.rst = HDL.Input()

        @HDL.seq
        def update_ff(s, posedge=(("clk",), "rst")):  # pragma: no cover
            ...

    _check_error(NestedTupleEdge(), r"'posedge' must be a string or tuple")

    # Auto edge conflicts in tuple
    class AutoEdgeTupleConflict(HDL.RawModule):
        _auto_pos_edges = ("clk",)
        _auto_neg_edges = ("rst_n",)

        @HDL.build
        def build_all(s):
            s.clk2 = HDL.Input()
            s.data = HDL.Logic()

        @HDL.seq
        def update_ff(
            s, posedge=("clk", "clk2"), negedge="rst_n"
        ):  # pragma: no cover
            s.data <<= 1

    _check_error(AutoEdgeTupleConflict(), r"'clk' is already an automatic")

    # Duplicate signal in edge tuple
    class DupEdgeTuple(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk1 = HDL.Input()
            s.clk2 = HDL.Input()
            s.data = HDL.Logic()

        @HDL.seq
        def update_ff(s, posedge=("clk1", "clk2", "clk1")):  # pragma: no cover
            s.data <<= 1

    _check_error(DupEdgeTuple(), r"'clk1' appears multiple times in posedge")

    # Undefined signal for edge argument
    class UndefSignalEdge(HDL.RawModule):
        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            ...

    _check_error(UndefSignalEdge(), r"Signal 'clk' not found")

    class UndefSignalTupleEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()

        @HDL.seq
        def update_ff(s, negedge=("clk", "rst")):  # pragma: no cover
            ...

    _check_error(UndefSignalTupleEdge(), r"Signal 'rst' not found")

    # Not signal for edge argument
    class NotSignalEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = 0

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            ...

    _check_error(NotSignalEdge(), r"NotSignalEdge, 'clk' is not a signal")

    # Not port for edge argument
    class NotPortEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Logic()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            ...

    _check_error(NotPortEdge(), r"'clk' must be a 1-bit input port")

    # Not input port for edge argument
    class OutPortEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.rst = HDL.Output()

        @HDL.seq
        def update_ff(s, negedge=("clk", "rst")):  # pragma: no cover
            ...

    _check_error(OutPortEdge(), r"'rst' must be a 1-bit input port")

    # Not scalar signal for edge argument
    class NotScalarEdge(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input(8)

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            ...

    _check_error(NotScalarEdge(), r"'clk' must be a 1-bit input port")


def test_FunctionParser_nested_errors():
    # Nested function
    class NestedFunc(HDL.RawModule):
        @HDL.comb
        def update(s):
            def nested():  # pragma: no cover
                ...

    _check_error(NestedFunc(), r"Nested functions are not supported")

    # Nested class
    class NestedClass(HDL.RawModule):
        @HDL.comb
        def update(s):
            class Inner:  # pragma: no coverG
                ...

    _check_error(NestedClass(), r"Nested classes are not supported")


def test_FunctionParser_Assign_errors():
    # Assignment in seq block
    class SeqAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out = s.in1

    _check_error(SeqAssign(), r"Wrong .* @seq .*\.update_ff\(\)")

    # Assignment in comb block
    class CombAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out = s.in1

    _check_error(CombAssign(), r"Wrong .* @comb .*\.update\(\)")


def test_FunctionParser_AugAssign_op_errors():
    # Wrong assignment in seq block
    class SeqBadAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.in1 += s.in2

    _check_error(SeqBadAssign(), r"Wrong .* @seq .*\.update_ff\(\)")

    # Blocking assignment in seq block
    class SeqBA(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.in1 /= s.in2

    _check_error(SeqBA(), r"Wrong .* @seq .*\.update_ff\(\)")

    # Connection in seq block
    class SeqConnect(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out @= s.in1

    _check_error(SeqConnect(), r"Wrong .* @seq .*\.update_ff\(\)")

    # Wrong assignment in comb block
    class CombBadAssign(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            s.in1 += s.in2

    _check_error(CombBadAssign(), r"Wrong .* @comb .*\.update\(\)")

    # Non-blocking assignment in comb block
    class CombNBA(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            s.in1 <<= s.in2

    _check_error(CombNBA(), r"Wrong .* @comb .*\.update\(\)")

    # Connection in comb block
    class CombConnect(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out @= s.in1

    _check_error(CombConnect(), r"Wrong .* @comb .*\.update\(\)")


def test_FunctionParser_AugAssign_width_errors():
    # Integer is too large
    class LargeInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 256

    _check_error(LargeInt(), r"is too wide for 8 bits")

    # Integer is too small
    class SmallInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129

    _check_error(SmallInt(), r"is too wide for 8 bits")

    # Width mismatch in comb block
    class CombWidthMismatch(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1

    _check_error(CombWidthMismatch(), r" Width mismatch: Bits4 /= Bits8")

    # Width mismatch in seq block
    class SeqWidthMismatch(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out <<= s.in1

    _check_error(SeqWidthMismatch(), r" Width mismatch: Bits4 <<= Bits8")

    # Inferred width of expression
    class InferredWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (-1 ^ ~255) + s.in1

    _check_error(InferredWidth(), r" Width mismatch: Bits4 /= Bits8")

    # Width of boolean NOT
    class WidthBoolNot(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= not s.in_

    _check_error(WidthBoolNot(), r"Width mismatch: Bits8 /= Bits1")

    # Boolean expression
    class BoolExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 and s.in2

    _check_error(BoolExpr(), r"Boolean 'and' requires Bool\(\)")

    # Width of RHS cat()
    class WidthConcatRHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(4)
            s.b = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.a, s.b)

    _check_error(WidthConcatRHS(), r" Width mismatch: Bits4 /= Bits8")

    # Width of LHS cat()
    class WidthConcatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Output(4)
            s.b = HDL.Output(4)
            s.in1 = HDL.Input(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.a, s.b)[:] /= s.in1

    _check_error(WidthConcatLHS(), r" Width mismatch: Bits8 /= Bits4")


def test_FunctionParser_AugAssign_drive_errors():
    # Driven by @=, /=
    class ConnComb(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)
            s.out @= 0

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_**2

    _check_error(ConnComb(), r"'out' has been driven by @= in build_all")

    # Driven by port, /=
    class PortComb(HDL.RawModule):
        class Sub(HDL.RawModule):
            @HDL.build
            def build_sub(s):
                s.data = HDL.Input(4)
                s.result = HDL.Output(8)
                s.result @= cat(s.data, s.data)

        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)
            s.sub = PortComb.Sub(data=s.in_, result=s.out)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_**2

    _check_error(PortComb(), r"'out' has been driven by @= in build_all")

    # Driven by @=, <<=
    class ConnSeq(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)
            s.out @= 0

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out <<= s.in_**2

    _check_error(ConnSeq(), r"'out' has been driven by @= in build_all")

    # Driven by /=, /=
    class CombComb(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update1(s):  # pragma: no cover
            s.out /= 0

        @HDL.comb
        def update2(s):  # pragma: no cover
            s.out /= s.in_**2

    _check_error(CombComb(), r"'out' has been driven by /= in update1")

    # Driven by /=, <<=
    class CombSeq(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 0

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out <<= s.in_**2

    _check_error(CombSeq(), r"'out' has been driven by /= in update")

    # Driven by <<=, <<=
    class SeqSeq(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.seq
        def update_ff1(s, posedge="clk"):  # pragma: no cover
            s.out <<= 0

        @HDL.seq
        def update_ff2(s, posedge="clk"):  # pragma: no cover
            s.out <<= s.in_**2

    _check_error(SeqSeq(), r"'out' has been driven by <<= in update_ff1")

    # Driven by <<=, /=
    class SeqComb(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            s.out <<= 0

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_**2

    _check_error(SeqComb(), r"'out' has been driven by /= in update")

    # Driven by @=, /= with cat() LHS
    class ConnCombConatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)
            s.out2 @= 0

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[:] /= s.in_**2

    _check_error(ConnCombConatLHS(), r"'out2' .* driven by @= in build_all")

    # Driven by @=, <<= with cat() LHS
    class ConnSeqConcatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.clk = HDL.Input()
            s.in_ = HDL.Input(4)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)
            s.out1 @= 0

        @HDL.seq
        def update_ff(s, posedge="clk"):  # pragma: no cover
            cat(s.out1, s.out2)[:] <<= s.in_**2

    _check_error(ConnSeqConcatLHS(), r"'out1' .* driven by @= in build_all")


def test_FunctionParser_Match_errors():
    # Integer subject
    class IntSubject(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match 123 & 3:
                case 0:
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(IntSubject(), r"Match subject cannot be a constant")

    # Bits subject
    class BitsSubject(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match b4(10) + b4(5):
                case 0:
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(BitsSubject(), r"Match subject cannot be a constant")

    # Global constant subject
    class GlobalConstSubject(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match CONST_INT + 2:
                case 0:
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(GlobalConstSubject(), r"Match subject cannot be a constant")

    # MatchAs: Variable capture with name only
    class CaptureWildcard(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case _ as x:
                    s.out /= 1

    _check_error(CaptureWildcard(), r"Variable capture.*not supported")

    # MatchAs: Variable capture with pattern
    class CaptureValue(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case 1 as x:
                    s.out /= 1
                case _:
                    s.out /= 2

    _check_error(CaptureValue(), r"Variable capture.*not supported")

    # MatchClass: Bits type pattern
    class BitsPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case b2(0):
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(BitsPattern(), r"must be an integer or a bit pattern")

    # MatchSingleton: Boolean pattern
    class BoolPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case False:
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(BoolPattern(), r"must be an integer or a bit pattern")

    # MatchSequence: List pattern
    class ListPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case [1, 2]:  # noqa: E211
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(ListPattern(), r"must be an integer or a bit pattern")

    # MatchMapping: Dict pattern
    class DictPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case {0: 1}:
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(DictPattern(), r"must be an integer or a bit pattern")

    # MatchOr: OR pattern
    class OrPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0 | 1:
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(OrPattern(), r"must be an integer or a bit pattern")


def test_FunctionParser_Match_pattern_errors():
    # Guard in match case
    class GuardPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.enable = HDL.Input(1)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0 if s.enable:
                    s.out /= 0
                case _:
                    s.out /= 1

    _check_error(GuardPattern(), r"Guards in match cases are not supported")

    # Bad integer width
    class BadIntWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 4:
                    s.out /= 0
                case 1:
                    s.out /= 1
                case _:
                    s.out /= 2

    _check_error(BadIntWidth(), r"4 \(0x4\) is too wide for 2 bits")

    # Empty pattern string
    class EmptyPatternStr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(EmptyPatternStr(), r"Empty bit pattern")

    # Empty bit pattern
    class EmptyBitPattern(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "__":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(EmptyBitPattern(), r"Empty bit pattern")

    # Invalid bit pattern
    class InvalidBitPat1(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "10X2":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(InvalidBitPat1(), r"Invalid bit pattern '10X2'")

    class InvalidBitPat2(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "10 11":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(InvalidBitPat2(), r"Invalid bit pattern '10 11'")

    class InvalidBitPat3(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "10_1z":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(InvalidBitPat3(), r"Invalid bit pattern '10_1z'")

    # Bad bit pattern width
    class BadBitPatWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case "10?01":
                    s.out /= 0
                case _:
                    s.out /= 2

    _check_error(BadBitPatWidth(), r"width mismatch: expected 4, got 5")

    # Pass followed by statements in default case
    class DefaultPassOther(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case _:
                    pass
                    s.out /= 1

    _check_error(DefaultPassOther(), r"empty default .* another statement")


def test_FunctionParser_Match_complete_errors():
    # Duplicate integer pattern
    class DupInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case 1:
                    s.out /= 1
                case 1:
                    s.out /= 2

    _check_error(DupInt(), r"Duplicate pattern 1 in match statement")

    # Miss 1 pattern
    class Miss1Int(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case 1:
                    s.out /= 2
                case 3:
                    s.out /= 3

    _check_error(Miss1Int(), r"- Missing 1 patterns: 2")

    # Miss 3 patterns
    class Miss3Int(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(2)
            s.out = HDL.Output(2)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0

    _check_error(Miss3Int(), r"- Missing 3 patterns: 1, 2, 3")

    # Miss 5 patterns
    class Miss5Int(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(3)
            s.out = HDL.Output(3)

        @HDL.comb
        def update(s):  # pragma: no cover
            match s.in_:
                case 0:
                    s.out /= 0
                case 2:
                    s.out /= 2
                case 4:
                    s.out /= 4

    _check_error(Miss5Int(), r"- Missing 5 patterns: 1, 3, 5, \.\.\.")


GLOBAL_VAR = 1


def test_FunctionParser_For_errors():
    # Else body
    class ForElse(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                ...
            else:
                pass

    _check_error(ForElse(), r"For-else is not supported in behavioral blocks")

    # Attribute in loop variable
    class AttrLoopVar(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for s.i in range(4):
                ...

    _check_error(AttrLoopVar(), r"For loop variable must be a simple name")

    # Same loop variable for nested loops
    class SameLoopVar(HDL.RawModule):
        @HDL.build
        def build(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(8):
                for i in range(4):
                    s.out[i] /= i & 1

    _check_error(SameLoopVar(), r"'i' conflicts with an existing symbol")

    # Global variable as loop variable
    class GlobalLoopVar(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for GLOBAL_VAR in range(4):
                ...

    _check_error(GlobalLoopVar(), r"'GLOBAL_VAR' conflicts with an existing")

    # b<N> as loop variable
    class BnLoopVar(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for b7 in range(4):
                ...

    _check_error(BnLoopVar(), r"'b7' conflicts with an existing symbol")

    # System function as loop variable
    class SysFuncLoopVar(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for range in range(4):  # noqa: F823
                ...

    _check_error(SysFuncLoopVar(), r"'range' conflicts with an existing")

    # HDL function as loop variable
    class HDLFuncLoopVar(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for rep in range(4):  # noqa: F402
                ...

    _check_error(HDLFuncLoopVar(), r"'rep' conflicts with an existing symbol")

    # Not range()
    class ForNotRange(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for i in [0, 1, 2, 3]:
                ...

    _check_error(ForNotRange(), r"For loop must iterate over range")

    # Break
    class ForBreak(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                if i == 2:
                    break
                ...

    _check_error(ForBreak(), r"Break statement is not supported in for loops")

    # Continue
    class ForContinue(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                if i == 2:
                    continue
                ...

    _check_error(ForContinue(), r"Continue .* not supported in for loops")


def test_FunctionParser_For_i32_var_errors():
    # Implicit extension of loop variable
    class I32VarImplicitExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(64)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out /= i

    _check_error(I32VarImplicitExt(), r" Width mismatch: Bits64 /= Bits32")

    # Extension of loop variable
    class I32VarExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(64)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out /= i.ext(64)

    _check_error(I32VarExt(), r"No attribute 'ext' for integer expressions")

    # Attribute of loop variable
    class I32VarAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(32)
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out[i] /= s.in_[31 - i.S]

    _check_error(I32VarAttr(), r"No attribute 'S' for integer expressions")

    # Attribute of forced i32 expression
    class I32ExprAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(32)
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out[i] /= s.in_[(-i + 31).P]

    _check_error(I32ExprAttr(), r"No attribute 'P' for integer expressions")

    # Index of loop variable
    class I32VarIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(32)
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out[i] /= s.in_[i[0]]

    _check_error(I32VarIndex(), r"Integer .* do not support bit-select")

    # Slice of forced i32 expression
    class I32ExprSlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(32)
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out[i] /= s.in_[(-i)[:5]]

    _check_error(I32ExprSlice(), r"Integer .* do not support part-select")

    # Part-select of forced i32 expression
    class I32ExprPartSel(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(32)
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(32):
                s.out[i] /= s.in_[(-i + 31)[5, -5]]

    _check_error(I32ExprPartSel(), r"Integer .* do not support part-select")

    # forced_i32 ** constant
    class I32ExprPow(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                s.out[i] /= s.in_[(i & 3) ** 2]

    _check_error(I32ExprPow(), r"Cannot replicate an integer expression")

    # forced_i32.ext()
    class I32ExprExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                s.out[i] /= s.in_[(i | 3).ext(33)]

    _check_error(I32ExprExt(), r"No attribute 'ext' for integer expressions")

    # cat() with forced i32 expression
    class I32ExprCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                s.out /= cat(s.in_, i + 1)

    _check_error(I32ExprCat(), r"Cannot concatenate an integer expression")

    # LHS cat() with loop variable
    class I32VarCatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                cat(s.out, i)[:] /= s.in_

    _check_error(I32VarCatLHS(), r"Cannot concatenate an integer expression")

    # rep() with forced i32 expression
    class I32ExprRep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(4):
                s.out /= rep(2, s.in_, i + 1)

    _check_error(I32ExprRep(), r"Cannot replicate an integer expression")


def test_FunctionParser_Constant_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, 1)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a constant")

    # Integer is too large
    class LargeInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 256

    _check_error(LargeInt(), r"is too wide for 8 bits")

    # Integer is too small
    class SmallInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129

    _check_error(SmallInt(), r"is too wide for 8 bits")

    # String constant as standalone statement
    class StrOnly(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            "hello"

    _check_error(StrOnly(), r"String constants are only allowed in match")

    # String constant in assignment
    class AssignStr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= "hello"

    _check_error(AssignStr(), r"String constants are only allowed in match")

    # String constant in expression
    class StrExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ + "hello"

    _check_error(StrExpr(), r"String constants are only allowed in match")

    # Float constant
    class FloatConst(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 3.14

    _check_error(FloatConst(), r"Unsupported constant type 'float'")

    # None constant
    class NoneConst(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= None

    _check_error(NoneConst(), r"Unsupported constant type 'NoneType'")


def test_FunctionParser_Name_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, TRUE)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to Bits constant 'TRUE'")

    # Undefined symbol
    class Undefined(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= undefined

    _check_error(Undefined(), r"Undefined symbol 'undefined'")


CONST_INT = 128
CONST_BITS = b4(8)


def test_FunctionParser_Name_global_errors():
    # Integer constant in LHS cat()
    class LHSCatInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, CONST_INT)[:] /= s.in_**4

    _check_error(LHSCatInt(), r"Cannot assign to integer constant 'CONST_INT'")

    # Bits constant in LHS cat()
    class LHSCatBits(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, CONST_BITS)[:] /= s.in_**4

    _check_error(LHSCatBits(), r"Cannot assign to Bits constant 'CONST_BITS'")


def test_FunctionParser_Name_global_i32_errors():
    # Implicit extension of integer constant
    class I32ImplicitExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(64)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= CONST_INT

    _check_error(I32ImplicitExt(), r" Width mismatch: Bits64 /= Bits32")

    # Extension of integer constant
    class I32Ext(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(64)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= CONST_INT.ext(64)

    _check_error(I32Ext(), r"No attribute 'ext' for integer expressions")

    # Attribute of integer constant
    class I32Attr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 31 - CONST_INT.S

    _check_error(I32Attr(), r"No attribute 'S' for integer expressions")

    # Attribute of forced i32 expression
    class I32ExprAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(32)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (-CONST_INT + 31).P

    _check_error(I32ExprAttr(), r"No attribute 'P' for integer expressions")

    # Index of integer constant
    class I32Index(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= CONST_INT[0]

    _check_error(I32Index(), r"Integer .* do not support bit-select")

    # Slice of forced i32 expression
    class I32ExprSlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(5)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (-CONST_INT)[:5]

    _check_error(I32ExprSlice(), r"Integer .* do not support part-select")

    # Part-select of forced i32 expression
    class I32ExprPartSel(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(5)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (-CONST_INT + 31)[5, -5]

    _check_error(I32ExprPartSel(), r"Integer .* do not support part-select")

    # forced_i32 ** constant
    class I32ExprPow(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (CONST_INT & 3) ** 2

    _check_error(I32ExprPow(), r"Cannot replicate an integer expression")

    # forced_i32.ext()
    class I32ExprExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(33)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (CONST_INT | 3).ext(33)

    _check_error(I32ExprExt(), r"No attribute 'ext' for integer expressions")

    # cat() with forced i32 expression
    class I32ExprCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.in_, CONST_INT + 1)

    _check_error(I32ExprCat(), r"Cannot concatenate an integer expression")

    # LHS cat() with integer constant
    class I32ConstCatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, CONST_INT)[:] /= s.in_

    _check_error(I32ConstCatLHS(), r"Cannot assign to integer constant")

    # rep() with forced i32 expression
    class I32ExprRep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(2, s.in_, CONST_INT + 1)

    _check_error(I32ExprRep(), r"Cannot replicate an integer expression")


def test_FunctionParser_Attribute_errors():
    # No attribute
    class NoAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.missing /= s.in1

    _check_error(NoAttr(), r"Attribute 'missing' not found .* NoAttr")

    # Unsupported attribute type
    class BadAttrType(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.num = 8

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.num

    _check_error(BadAttrType(), r"Type of attribute 'num' is not supported")

    # Attribute of input port
    class InputAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.data_bits

    _check_error(InputAttr(), r"Cannot access attribute 'data_bits'")

    # Attribute of output port
    class OutputAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out.data /= s.in_

    _check_error(OutputAttr(), r"Cannot access attribute 'data'")

    # Attribute of Logic
    class LogicAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.logic = HDL.Logic(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.logic.data_bits

    _check_error(LogicAttr(), r"Cannot access attribute 'data_bits'")

    # Submodule only
    class SubmoduleOnly(HDL.RawModule):
        class Sub(HDL.RawModule):
            @HDL.build
            def build_sub(s):
                s.in_ = HDL.Input(8)
                s.out = HDL.Output(8)

        @HDL.build
        def build_all(s):
            s.result = HDL.Output(8)
            s.sub = SubmoduleOnly.Sub(0)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.result /= s.sub

    _check_error(SubmoduleOnly(), r"Cannot use a submodule .* as operand")

    # Assign to input port
    class AssignInput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.in_ /= 0xAB

    _check_error(AssignInput(), r"Cannot assign to input port 'in_'")


def test_FunctionParser_Attribute_submodule_errors():
    class Sub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input()
            s.out = HDL.Output()
            s.tmp = HDL.Logic()
            s.out @= s.in_

    # No attribute
    class NoAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1, s.out)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.sub.missing /= s.in1

    _check_error(NoAttr(), r"Attribute 'missing' not found .* 'sub'")

    # Not circuit object
    class NotCircuitObj(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.sub.is_module

    _check_error(NotCircuitObj(), r"'is_module' .* 'sub' is not a port")

    # Not port
    class NotPort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.sub.tmp

    _check_error(NotPort(), r"'tmp' .* 'sub' is not a port")

    # Read submodule input port
    class ReadInputPort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.sub.in_

    _check_error(ReadInputPort(), r"read submodule input port 'sub.in_'")

    # Assign to submodule output port
    class AssignOutputPort(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()
            s.sub = Sub(s.in1)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.sub.out /= s.in1

    _check_error(AssignOutputPort(), r"assign to .* output port 'sub.out'")


def test_FunctionParser_Attribute_bits_property_errors():
    # At LHS
    class AtLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.tmp = HDL.Logic(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.tmp.S /= s.in_**2

    _check_error(AtLHS(), r"Cannot assign to property 'S'")

    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)
            s.tmp = HDL.Logic(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.tmp /= s.in_
            cat(s.out, s.tmp.S)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to property 'S'")

    # Signed value only
    class SignedOnly(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.in_.S

    _check_error(SignedOnly(), r"only allowed in comparison or shift")

    # Connect from signed value
    class ConnectSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in_.S

    _check_error(ConnectSigned(), r"only allowed in comparison or shift")

    # Assign from signed value
    class AssignSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.S

    _check_error(AssignSigned(), r"only allowed in comparison or shift")

    # Attribute of signed value
    class SignedAttrS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.S.S

    _check_error(SignedAttrS(), r"only allowed in comparison or shift")

    class SignedAttrAO(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.S.AO

    _check_error(SignedAttrAO(), r"only allowed in comparison or shift")

    # Signed value as index
    class SignedIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.sel = HDL.Input(3)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.sel.S]

    _check_error(SignedIndex(), r"only allowed in comparison or shift")

    # Signed value as slice
    class SignedSlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b3(0).S : 4]

    _check_error(SignedSlice(), r"only allowed in comparison or shift")

    # Signed value as part-select base
    class SignedPartBase(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.sel = HDL.Input(3)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.sel.S, 4]

    _check_error(SignedPartBase(), r"only allowed in comparison or shift")

    # Signed value as part-select width
    class SignedPartWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[7, b3(-4).S]

    _check_error(SignedPartWidth(), r"only allowed in comparison or shift")

    # Unary operation with signed value
    class UnaryOpSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= ~s.in_.S

    _check_error(UnaryOpSigned(), r"only allowed in comparison or shift")

    # Binary operation with signed value
    class BinOpSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)
            s.out @= s.in1.S + s.in2

    _check_error(BinOpSigned(), r"only allowed in comparison or shift")

    # Boolean operation with signed value
    class BoolOpSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.in1.S and s.in2)

    _check_error(BoolOpSigned(), r"only allowed in comparison or shift")

    # Conditional expression with signed value
    class CondExprSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.sel = HDL.Input()
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1.S if s.sel else s.in2

    _check_error(CondExprSigned(), r"only allowed in comparison or shift")

    # Function argument with signed value
    class FuncArgSigned(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.in_.S)

    _check_error(FuncArgSigned(), r"only allowed in comparison or shift")


def test_FunctionParser_Attribute_bits_method_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)
            s.tmp = HDL.Logic(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.tmp /= s.in_
            cat(s.out, s.tmp.ext(8))[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to result of method ext\(\)")


def test_FunctionParser_Attribute_array_errors():
    # At LHS
    class AtLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.mem /= s.in_

    _check_error(AtLHS(), r"cannot be used without indexing")

    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_
            cat(s.out, s.mem)[:] /= s.in_**2

    _check_error(LHSCat(), r"cannot be used without indexing")

    # Array only
    class ArrayOnly(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.mem

    _check_error(ArrayOnly(), r"cannot be used without indexing")

    # Assign from array
    class AssignArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem

    _check_error(AssignArray(), r"cannot be used without indexing")

    # Attribute of array
    class ArrayAttr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem.nbits

    _check_error(ArrayAttr(), r"cannot be used without indexing")

    # Array as index
    class ArrayIndex(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(3) @ 8
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.mem]

    _check_error(ArrayIndex(), r"cannot be used without indexing")

    # Array as slice
    class ArraySlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(3) @ 8
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.mem : 4]

    _check_error(ArraySlice(), r"cannot be used without indexing")

    # Array as part-select base
    class ArrayPartBase(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(3) @ 8
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.mem, 4]

    _check_error(ArrayPartBase(), r"cannot be used without indexing")

    # Array as part-select width
    class ArrayPartWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.mem = HDL.Logic(3) @ 8
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[7, s.mem]

    _check_error(ArrayPartWidth(), r"cannot be used without indexing")

    # Unary operation with array
    class UnaryOpArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.mem = HDL.Logic(8) @ 16
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= ~s.mem

    _check_error(UnaryOpArray(), r"cannot be used without indexing")

    # Binary operation with array
    class BinOpArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.mem1 = HDL.Logic(8) @ 16
            s.mem2 = HDL.Logic(8) @ 16
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem1 + s.mem2

    _check_error(BinOpArray(), r"cannot be used without indexing")

    # Boolean operation with array
    class BoolOpArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.mem1 = HDL.Logic(8) @ 16
            s.mem2 = HDL.Logic(8) @ 16
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.mem1 and s.mem2)

    _check_error(BoolOpArray(), r"cannot be used without indexing")

    # Conditional expression with array
    class CondExprArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.sel = HDL.Input()
            s.mem1 = HDL.Logic(8) @ 16
            s.mem2 = HDL.Logic(8) @ 16
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem1 if s.sel else s.mem2

    _check_error(CondExprArray(), r"cannot be used without indexing")

    # Function argument with array
    class FuncArgArray(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.mem = HDL.Logic(8) @ 16
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.mem)

    _check_error(FuncArgArray(), r"cannot be used without indexing")


def test_FunctionParser_Subscript_errors():
    # Bit-select ConcatLHS
    class IndexConcatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[0] /= s.in_[0]

    _check_error(IndexConcatLHS(), r"only supports complete assignment")

    # Constant part-select ConcatLHS
    class SliceConcatLHS1(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[:7] /= s.in_

    _check_error(SliceConcatLHS1(), r"only supports complete assignment")

    class SliceConcatLHS2(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[::1] /= s.in_

    _check_error(SliceConcatLHS2(), r"only supports complete assignment")

    class SliceConcatLHS3(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[0:] /= s.in_

    _check_error(SliceConcatLHS3(), r"only supports complete assignment")

    # Indexed part-select ConcatLHS
    class PartSelConcatLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out1 = HDL.Output(4)
            s.out2 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out1, s.out2)[4, 4] /= s.in_

    _check_error(PartSelConcatLHS(), r"only supports complete assignment")


def test_FunctionParser_Subscript_array_errors():
    # Array slice operation
    class ArraySlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.addr = HDL.Input(4)
            s.out = HDL.Output(4)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[4:8]

    _check_error(ArraySlice(), r"Array does not support part-select")

    # Array tuple part-select operation
    class ArrayPartSel(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.addr = HDL.Input(4)
            s.start = HDL.Input(4)
            s.out = HDL.Output(4)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[s.start, 4]

    _check_error(ArrayPartSel(), r"Array does not support part-select")

    # Integer index is out of range - upper bound
    class ArrayLargeInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[16]

    _check_error(ArrayLargeInt(), r"Index 16 is out of range \[0, 15\]")

    # Integer index is out of range - lower bound
    class ArraySmallInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[-1]

    _check_error(ArraySmallInt(), r"Index -1 is out of range \[0, 15\]")

    # Bits constant index is out of range
    class ArrayBadBits(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[b8(16)]

    _check_error(ArrayBadBits(), r"Index 16 is out of range \[0, 15\]")

    # Bits constant expression index is out of range
    class ArrayBadBitsExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.mem = HDL.Logic(8) @ 8

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[b4(3) + b4(5)]

    _check_error(ArrayBadBitsExpr(), r"Index 8 is out of range \[0, 7\]")

    # Variable index width too wide for 2^n array size
    class ArrayBadVar(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.idx = HDL.Input(5)
            s.mem = HDL.Logic(8) @ 16

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[s.idx]

    _check_error(ArrayBadVar(), r"width 5 is too wide for range \[0, 15\]")

    # Variable expression index width too wide for non-2^n array size
    class ArrayBadVarExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)
            s.idx1 = HDL.Input(2)
            s.idx2 = HDL.Input(2)
            s.mem = HDL.Logic(8) @ 6  # non-2^n

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.mem[cat(s.idx1, s.idx2)]  # 4-bit index

    _check_error(ArrayBadVarExpr(), r"width 4 is too wide for range \[0, 5\]")


def test_FunctionParser_Subscript_indexable_errors():
    # Bit-select integer
    class IndexInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 0xFF[3]

    _check_error(IndexInt(), r"Value does not support bit-select")

    # Constant part-select integer
    class SliceInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 0xFF[4:7]

    _check_error(SliceInt(), r"Value does not support part-select")

    # Indexed part-select integer
    class PartSelInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 0xFF[4, 4]

    _check_error(PartSelInt(), r"Value does not support part-select")

    # Scalar input
    class ScalarInput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[0]

    _check_error(ScalarInput(), r"Value does not support bit-select")

    # Scalar output
    class ScalarOutput(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out[:] /= s.in_

    _check_error(ScalarOutput(), r"Value does not support part-select")

    # Scalar logic
    class ScalarLogic(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.scalar = HDL.Logic()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.scalar[0, 1]

    _check_error(ScalarLogic(), r"Value does not support part-select")

    # Bits constant
    class BitsConst(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= b8(0xFF)[3]

    _check_error(BitsConst(), r"Value does not support bit-select")

    # Bits expression
    class BitsExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (b8(0xFF) & 0xAB)[0:4]

    _check_error(BitsExpr(), r"Value does not support part-select")

    # Vector expression
    class VecExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.vec = HDL.Logic(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (~s.vec)[0, 4]

    _check_error(VecExpr(), r"Value does not support part-select")

    # Reduction
    class Reduction(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.AO[0]

    _check_error(Reduction(), r"Value does not support bit-select")

    # Concat
    class Concat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(4)
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.in1, s.in2)[2:6]

    _check_error(Concat(), r"Value does not support part-select")

    # Replicate
    class Replicate(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(4)
            s.in_ = HDL.Input(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(2, s.in_, s.in_[:2])[2, 4]

    _check_error(Replicate(), r"Value does not support part-select")


def test_FunctionParser_Subscript_slice_errors():
    # Slice step
    class SliceStep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out1 = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out1[::2] /= s.in1

    _check_error(SliceStep(), r"Part-select does not support slice step")

    # Lower bound is not an integer constant
    class VarLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.sel = HDL.Input(3)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1[s.sel :]

    _check_error(VarLower(), r"Lower bound must be an integer or Bits")

    # Lower bound is out of range
    class BadLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[-1:9]

    _check_error(BadLower(), r"Lower bound -1 .* range of \[0, 7\]")

    # Lower bound expression is out of range
    class BadLowerExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4 - 5 : 8]

    _check_error(BadLowerExpr(), r"Lower bound -1 .* range of \[0, 7\]")

    # Upper bound is not an integer constant
    class VarUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.sel = HDL.Input(3)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1[: s.sel]

    _check_error(VarUpper(), r"Upper bound must be an integer or Bits")

    # Upper bound is out of range
    class BadUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[0:9]

    _check_error(BadUpper(), r"Upper bound 9 .* range of \[1, 8\]")

    # Upper bound expression is out of range
    class BadUpperExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[0 : 8 + 1]

    _check_error(BadUpperExpr(), r"Upper bound 9 .* range of \[1, 8\]")

    # Empty slice
    class EmptySlice(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[5:5]

    _check_error(EmptySlice(), r"Upper bound must be greater than lower")

    # Upper < lower
    class BadOrder(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output()
            s.in_ = HDL.Input(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[5:4]

    _check_error(BadOrder(), r"Upper bound must be greater than lower bound")


def test_FunctionParser_Subscript_part_select_errors():
    # Less tuple elements
    class LessTupleElems(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[(4,)]

    _check_error(LessTupleElems(), r"Indexed part-select requires a tuple")

    # More tuple elements
    class MoreTupleElems(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, 4, 1, True]

    _check_error(MoreTupleElems(), r"Indexed part-select requires a tuple")

    # Direction
    #
    # Integer direction
    class IntDir(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, 4, 1]

    _check_error(IntDir(), r"direction must be a Bits1 .*DESC")

    # Bits8 direction
    class Bits8Dir(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, 4, b8(1)]

    _check_error(Bits8Dir(), r"direction must be a Bits1 .*DESC")

    # Bits expression direction
    class BitsExprDir(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)
            s.out @= s.in_[4, 4, TRUE | TRUE]  # valid in AssemblerHDL

    _check_error(BitsExprDir(), r"direction must be a Bits1 .*DESC")

    # Negative Bits width with DESC
    class NegBitsWidthDesc(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, -b8(4), DESC]

    _check_error(NegBitsWidthDesc(), r"integer width or explicit DESC")

    # Negative Bits expression width with DESC
    class NegBitsExprWidthDesc(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, -(b8(4) - b8(8)), DESC]

    _check_error(NegBitsExprWidthDesc(), r"integer width or explicit DESC")

    # Negative integer width with DESC
    class NegIntWidthDesc(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, -4, DESC]

    _check_error(NegIntWidthDesc(), r"Descending .* width must be a positive")

    # Negative integer expression width with DESC
    class NegIntExprWidthDesc(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[4, 4 - 8, DESC]

    _check_error(NegIntExprWidthDesc(), r"width must be a positive")

    # Start index
    #
    # Integer is out of range
    class BadIntStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[8, -4]

    _check_error(BadIntStart(), r"Start index 8 is out of range \[0, 7\]")

    # Integer expression is out of range
    class BadIntExprStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[7 + 1, -4]

    _check_error(BadIntExprStart(), r"Start index 8 is out of range \[0, 7\]")

    # Bits constant index is out of range
    class BadBitsStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(8), 4]

    _check_error(BadBitsStart(), r"Start index 8 is out of range \[0, 7\]")

    # Variable index width too wide for 2^n target
    class BadVarStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.idx, 4]

    _check_error(BadVarStart(), r"Start index .* too wide for range \[0, 7\]")

    # Variable expression index width too wide for non-2^n target
    class BadVarExprStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(5)  # 5-bit target (non-2^n, threshold=10)
            s.idx1 = HDL.Input(2)
            s.idx2 = HDL.Input(2)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[cat(s.idx1, s.idx2), -4]

    _check_error(BadVarExprStart(), r"index .* too wide for range \[0, 4\]")

    # Width
    #
    # Variable width
    class VarWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.width = HDL.Input(3)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[0, s.width]

    _check_error(VarWidth(), r"Part-select width must be a constant")

    # Variable expression as width
    class VarExprWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.width = HDL.Input(3)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[2, s.width - 3, DESC]

    _check_error(VarExprWidth(), r"Part-select width must be a constant")

    # Lower bound is out of range, int width
    class BadIntLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[2, -4]

    _check_error(BadIntLower(), r"Part-select \[2 -: 4\] lower bound -1")

    # Lower bound is out of range, bits width
    class BadBitsLower(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[2, b3(4), DESC]

    _check_error(BadBitsLower(), r"Part-select \[2 -: 4\] lower bound -1")

    # Upper bound is out of range, int expression width
    class BadIntExprUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[6, 2 + 1]

    _check_error(BadIntExprUpper(), r"Part-select \[6 \+: 3\] upper bound 8")

    # Upper bound is out of range, bits expression width
    class BadBitsExprUpper(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[6, b3(2) + b3(1)]

    _check_error(BadBitsExprUpper(), r"Part-select \[6 \+: 3\] upper bound 8")


def test_FunctionParser_Subscript_index_errors():
    # Integer index is out of range
    class BadInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[8]

    _check_error(BadInt(), r"Index 8 is out of range \[0, 7\]")

    # Integer expression index is out of range
    class LargeIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[7 + 1]

    _check_error(LargeIntExpr(), r"Index 8 is out of range \[0, 7\]")

    class SmallIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[7 - 8]

    _check_error(SmallIntExpr(), r"Index -1 is out of range \[0, 7\]")

    # Bits constant index is out of range
    class BadBits(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(8)]

    _check_error(BadBits(), r"Index 8 is out of range \[0, 7\]")

    # Bits constant expression index is out of range
    class BadBitsExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b4(3) + b4(2)]

    _check_error(BadBitsExpr(), r"Index 5 is out of range \[0, 3\]")

    # Variable index width too wide for 2^n target
    class BadVar(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.idx = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[s.idx]

    _check_error(BadVar(), r"Index width 4 is too wide for range \[0, 7\]")

    # Variable expression index width too wide for non-2^n target
    class BadVarExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(5)  # 5-bit target (non-2^n, threshold=10)
            s.idx1 = HDL.Input(2)
            s.idx2 = HDL.Input(2)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[cat(s.idx1, s.idx2)]

    _check_error(BadVarExpr(), r"Index width 4 is too wide for range \[0, 4\]")


# Test constant expression evaluation
def test_FunctionParser_Subscript_index_const_expr_errors():
    # ast.Name
    class ExprTRUE(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[TRUE**8]

    _check_error(ExprTRUE(), r"Index 255 is out of range \[0, 7\]")

    # ast.Attribute
    class ExprReduce(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[(b8(0x0F) | b8(0xF0)).AO ** 4]

    _check_error(ExprReduce(), r"Index 15 is out of range \[0, 7\]")

    # ast.UnaryOp
    #
    class ExprInvert(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[~b8(7)]

    _check_error(ExprInvert(), r"Index 248 is out of range \[0, 7\]")

    class ExprNot(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(1) + (not b8(1))]

    _check_error(ExprNot(), r"Width mismatch: Bits8 \+ Bits1")

    class ExprUSub(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[-b8(1)]

    _check_error(ExprUSub(), r"Index 255 is out of range \[0, 7\]")

    # ast.BinOp
    #
    class ExprBitOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(8) | b8(3) & (b8(2) ^ b8(1))]

    _check_error(ExprBitOp(), r"Index 11 is out of range \[0, 7\]")

    class ExprArithOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(8) + b8(3) - (+b8(2) + b8(1))]

    _check_error(ExprArithOp(), r"Index 8 is out of range \[0, 7\]")

    class ExprPow(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b4(1) ** 2]

    _check_error(ExprPow(), r"Index 17 is out of range \[0, 7\]")

    class ExprShift(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b4(1) << (b8(2) + 1)]

    _check_error(ExprShift(), r"Index 8 is out of range \[0, 7\]")

    # ast.BoolOp
    class ExprBoolOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[Bool(b8(1) and b8(2) and b8(3) or b8(4)) ** 8]

    _check_error(ExprBoolOp(), r"Index 255 is out of range \[0, 7\]")

    # ast.IfExp
    class ExprCond(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b8(8) + 2 if 5 > 3 else b8(2)]

    _check_error(ExprCond(), r"Index 10 is out of range \[0, 7\]")

    # ast.Compare
    class ExprCompare(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[
                (b8(1) != b8(2)) ** 4 << (b4(0xA) > (b4(5) + b4(4)))
            ]

    _check_error(ExprCompare(), r"Index 14 is out of range \[0, 7\]")

    # ast.Call
    #
    class ExprZExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b4(10).ext(8)]

    _check_error(ExprZExt(), r"Index 10 is out of range \[0, 7\]")

    class ExprSExt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[b2(3).S.ext(4)]

    _check_error(ExprSExt(), r"Index 15 is out of range \[0, 7\]")

    class ExprCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[cat(b2(1), b2(3), b2(3))]

    _check_error(ExprCat(), r"Index 31 is out of range \[0, 7\]")

    class ExprRep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_[rep(2, b2(0), b2(1))]

    _check_error(ExprRep(), r"Index 17 is out of range \[0, 7\]")


def test_FunctionParser_UnaryOp_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, ~s.out)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a unary expression")

    # Integer is too large, checked in assignment
    class LargeInt_inAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= ~256

    _check_error(LargeInt_inAssign(), r"is too wide for 8 bits")

    # Integer is too small, checked in assignment
    class SmallInt_inAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129

    _check_error(SmallInt_inAssign(), r"is too wide for 8 bits")

    # Integer expression is too large, checked in BinOp
    class LargeInt_atBinRight(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):
            s.out /= s.in_ ^ ~(255 + 1)

    _check_error(LargeInt_atBinRight(), r"is too wide for 8 bits")

    # Integer expression is too small, checked in BinOp
    class SmallInt_atBinLeft(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -((-255) - 1) & s.in_

    _check_error(SmallInt_atBinLeft(), r"is too wide for 8 bits")


def test_FunctionParser_BinOp_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, b8(0) | b8(1))[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a binary expression")

    # Unsupported binary operator
    class BadBinOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 @ s.in1

    _check_error(BadBinOp(), r"Operator '@' is not supported")

    # Integer is too large, width inferred from left
    class LargeIntRight(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 | 256

    _check_error(LargeIntRight(), r"is too wide for 8 bits")

    # Integer is too small, width inferred from right
    class SmallIntLeft(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129 ^ s.in1

    _check_error(SmallIntLeft(), r"is too wide for 8 bits")

    # Integer expression is too large
    class LargeIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 | ((256 & -1) + 1)

    _check_error(LargeIntExpr(), r"is too wide for 8 bits")

    # Integer expression is too small, checked in assignment
    class SmallInt_inAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -1 + -128

    _check_error(SmallInt_inAssign(), r"is too wide for 8 bits")

    # Integer is too large, checked in assignment
    class LargeInt_inAssign(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (255 & -1) + 1

    _check_error(LargeInt_inAssign(), r"is too wide for 8 bits")

    # Width mismatch
    class WidthMismatch(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 & s.in2

    _check_error(WidthMismatch(), r"Width mismatch: Bits8 & Bits4")


def test_FunctionParser_BinOp_pow_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, b8(0) ** 1)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a binary expression")

    # Replication (**) with integer as a part
    class RepIntPart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 0xF**4

    _check_error(RepIntPart(), r"Cannot replicate an integer constant")

    # Replication (**) count parameter as Bits
    class RepBitsCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ ** b8(2)

    _check_error(RepBitsCount(), r"Replication count must be an integer")

    # Replication (**) count parameter as variable
    class RepVarCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.count = HDL.Input(8)
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_**s.count

    _check_error(RepVarCount(), r"Replication count must be an integer")

    # Replication (**) count parameter as expression with variable
    class RepExprCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.count = HDL.Input(8)
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ ** (s.count + 1)

    _check_error(RepExprCount(), r"Replication count must be an integer")

    # Replication (**) count parameter as constant expression
    class RepConstExprCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ ** (b8(2) + 4)

    _check_error(RepConstExprCount(), r"Replication count must be an integer")

    # Replication (**) with negative count
    class RepNegCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_**-1

    _check_error(RepNegCount(), r"Replication count must be non-negative")

    # Replication (**) with negative count expression
    class RepNegCountExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ ** (4 - 5)

    _check_error(RepNegCountExpr(), r"Replication count must be non-negative")


def test_FunctionParser_BinOp_shift_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, b8(0) << 4)[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a binary expression")

    # Folding integer shift
    class FoldIntShift(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (4 + 6) << (4 + 1)  # 0xA << 5

    _check_error(FoldIntShift(), r"is too wide for 8 bits")

    # Non-integer amount for an integer
    class IntShiftBits(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 1 << b8(4)

    _check_error(IntShiftBits(), r"supports only integer .* amount")

    # Signed left shift
    class SignedLeftShift(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.S << 2

    _check_error(SignedLeftShift(), r"Signed value supports only right shift")

    # Shift amount
    #
    # Integer amount equals to width
    class BadInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ << 8

    _check_error(BadInt(), r"Shift amount 8 is out of range \[0, 7\]")

    # Integer amount is out of range
    class LargeInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ >> 10

    _check_error(LargeInt(), r"Shift amount 10 is out of range \[0, 7\]")

    # Integer expression amount out of range
    class LargeIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ << (7 + 1)

    _check_error(LargeIntExpr(), r"Shift amount 8 is out of range \[0, 7\]")

    class SmallIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ >> (3 - 5)

    _check_error(SmallIntExpr(), r"Shift amount -2 is out of range \[0, 7\]")

    # Bits constant amount out of range
    class BadBits(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ << b4(8)

    _check_error(BadBits(), r"Shift amount 8 is out of range \[0, 7\]")

    # Bits constant expression shift amount out of range
    class BadBitsExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ >> (b4(3) + b4(2))

    _check_error(BadBitsExpr(), r"Shift amount 5 is out of range \[0, 3\]")

    # Variable amount width too wide for 2^n value width
    class BadVar(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.shamt = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ << s.shamt

    _check_error(BadVar(), r"Shift amount width .* wide for range \[0, 7\]")

    # Variable expression amount width too wide for non-2^n value width
    class BadVarExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(5)  # 5-bit width (non-2^n, threshold=10)
            s.amt1 = HDL.Input(2)
            s.amt2 = HDL.Input(2)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_ >> cat(s.amt1, s.amt2)

    _check_error(BadVarExpr(), r"width 4 is too wide for range \[0, 4\]")


def test_FunctionParser_BoolOp_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, b8(0) or b8(1))[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a boolean expression")

    # Boolean expression without Bool() wrapper
    class NoBoolBit(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 and s.in2

    _check_error(NoBoolBit(), r"Boolean 'and' requires Bool\(\)")

    # Wrap unary operation with Bool()
    class BoolUnaryOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(4)
            s.b = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(~(s.a or s.b))

    _check_error(BoolUnaryOp(), r"Boolean 'or' requires Bool\(\)")

    # Wrap binary operation with Bool()
    class BoolBinOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(4)
            s.b = HDL.Input(4)
            s.c = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.a | (s.b and s.c))

    _check_error(BoolBinOp(), r"Boolean 'and' requires Bool\(\)")

    # Nested boolean expression separated by unary operation
    class NestedWithUnary(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(4)
            s.b = HDL.Input(4)
            s.c = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.a or ~(s.b and s.c))

    _check_error(NestedWithUnary(), r"Boolean 'and' requires Bool\(\)")

    # Nested boolean expression separated by binary operation
    class NestedWithBinOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.a = HDL.Input(4)
            s.b = HDL.Input(4)
            s.c = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.a or (1 + (s.b and s.c)))

    _check_error(NestedWithBinOp(), r"Boolean 'and' requires Bool\(\)")

    # Mixed scalar value and vector in boolean operation
    class VecScalarV(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.scalar = HDL.Input()
            s.vector = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.vector or s.scalar

    _check_error(VecScalarV(), r"Boolean 'or' requires Bool\(\)")

    # Mixed scalar value and Bits in boolean operation
    class BitsScalarV(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.scalar = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= b8(1) and s.scalar

    _check_error(BitsScalarV(), r"Boolean 'and' requires Bool\(\)")

    # Scalar with integer in boolean operation
    class IntScalarV(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.scalar = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 5 or s.scalar

    _check_error(IntScalarV(), r"Boolean 'or' requires Bool\(\)")


def test_FunctionParser_IfExp_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(7)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, s.in_[0] if s.in_ != 0 else FALSE)[:] /= s.in_**2

    _check_error(LHSCat(), r"Cannot assign to a conditional expression")

    # Var ? int : int
    class VarIntInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= 42 if s.in_ > 100 else 24

    _check_error(VarIntInt(), r"Cannot infer width .* conditional expression")

    # Integer is too large, width inferred from left
    class LargeIntElse(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.sel = HDL.Input()
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 if s.sel else 256

    _check_error(LargeIntElse(), r"is too wide for 8 bits")

    # Integer is too small, width inferred from right
    class SmallIntLeft(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.sel = HDL.Input()
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129 if s.sel else s.in1

    _check_error(SmallIntLeft(), r"is too wide for 8 bits")

    # Integer expression is too large
    class LargeIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.sel = HDL.Input()
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 if s.sel else (256 & -1) + 1

    _check_error(LargeIntExpr(), r"is too wide for 8 bits")

    # Width mismatch
    class WidthMismatch(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.sel = HDL.Input()
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 if s.sel else s.in2

    _check_error(WidthMismatch(), r"Width mismatch: \<cond\> \? Bits8 : Bits4")


def test_FunctionParser_Compare_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(7)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, s.in_ == b4(0))[:] /= s.in_**2

    _check_error(LHSCat(), r"Cannot assign to a comparison expression")

    # Chained comparison
    class ChainedComp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.in3 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 < s.in2 < s.in3

    _check_error(ChainedComp(), r"single comparison \(a OP b\) is supported")

    # Unsupported comparison operator
    class BadCompOp(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input()
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 is s.in1

    _check_error(BadCompOp(), r"Operator 'is' is not supported")

    # Signed comparison with unsigned right operand
    class BadSignedCompRight(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1.S < s.in2

    _check_error(BadSignedCompRight(), r"requires both operands to be signed")

    # Signed comparison with unsigned left operand
    class BadSignedCompLeft(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 < s.in2.S

    _check_error(BadSignedCompLeft(), r"requires both operands to be signed")

    # Integer is too large
    class LargeIntRight(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 == 256

    _check_error(LargeIntRight(), r"is too wide for 8 bits")

    # Integer is too small, width inferred from right
    class SmallIntLeft(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= -129 < s.in1

    _check_error(SmallIntLeft(), r"is too wide for 8 bits")

    # Integer expression is too large
    class LargeIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 != ((256 & -1) + 1)

    _check_error(LargeIntExpr(), r"is too wide for 8 bits")

    # Width mismatch
    class WidthMismatch(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(8)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in1 >= s.in2

    _check_error(WidthMismatch(), r"Width mismatch: Bits8 >= Bits4")


def test_FunctionParser_Call_bits_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, b8(0))[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a Bits constant")

    # Bits constant, not b8()
    class BitsConst(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            Bits(8, 0)

    _check_error(BitsConst(), r"Use b<N>\(\) for Bits constants")

    # b<N> constant without argument
    class bConstNoArg(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            b8()

    _check_error(bConstNoArg(), r"b8\(\) requires exactly one argument")

    # b<N> constant with more arguments
    class bConstMoreArgs(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            b8(1, 2)

    _check_error(bConstMoreArgs(), r"b8\(\) requires exactly one argument")

    # b<N> constant with wrong argument
    class bConstWrongArg(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= b8(s.in_ + 1)

    _check_error(bConstWrongArg(), r"b8\(\) argument must be an integer")

    # Integer is too large
    class LargeInt(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            b8(256)

    _check_error(LargeInt(), r"is too wide for 8 bits")

    # Integer expression is too small
    class SmallIntExpr(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            b8(-128 - 1)

    _check_error(SmallIntExpr(), r"is too wide for 8 bits")


def test_FunctionParser_Call_bits_ext_errors():
    # No arguments
    class ExtNoArg(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.ext()

    _check_error(ExtNoArg(), r"ext\(\) requires exactly one argument, got 0")

    # More arguments
    class ExtMoreArgs(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.ext(16, 32)

    _check_error(ExtMoreArgs(), r"requires exactly one argument, got 2")

    # Variable width argument
    class ExtVarWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.width = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.ext(s.width)

    _check_error(ExtVarWidth(), r"argument must be an integer constant")

    # Bits width argument
    class ExtBitsWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= s.in_.ext(b8(16))

    _check_error(ExtBitsWidth(), r"argument must be an integer constant")

    # Small width argument
    class ExtSmallWidth(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= (s.in1 + s.in2).ext(4)

    _check_error(ExtSmallWidth(), r"must be greater than the current width 4")


def test_FunctionParser_Call_Bool_errors():
    # In LHS cat()
    class LHSCat(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            cat(s.out, Bool(1))[:] /= s.in_**4

    _check_error(LHSCat(), r"Cannot assign to a Bool\(\) expression")

    # More arguments for Bool()
    class BoolMoreArgs(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in1 = HDL.Input(4)
            s.in2 = HDL.Input(4)
            s.out = HDL.Output()

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= Bool(s.in1, s.in2)

    _check_error(BoolMoreArgs(), r"Bool\(\) .* one argument, got 2")


def test_FunctionParser_Call_cat_errors():
    # Less arguments for cat()
    class CatLessArgs(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.in_)

    _check_error(CatLessArgs(), r"cat\(\) requires .* two arguments, got 1")

    # cat() with integer argument
    class CatInt(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.in_, 0xF)

    _check_error(CatInt(), r"Cannot concatenate an integer constant")

    # cat() with integer expression argument
    class CatIntExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= cat(s.in_, 0xA | 0xF)

    _check_error(CatIntExpr(), r"Cannot concatenate an integer constant")


def test_FunctionParser_Call_rep_errors():
    # rep() at LHS
    class RepLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):
            rep(2, s.out)[:] /= s.in_

    _check_error(RepLHS(), r"Cannot assign to a rep\(\)")

    # Less arguments for rep()
    class RepLessArgs(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(2)

    _check_error(RepLessArgs(), r"rep\(\) requires .* two arguments, got 1")

    # rep() count parameter as Bits
    class RepBitsCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(b8(2), s.in_)

    _check_error(RepBitsCount(), r"rep\(\) count argument must be an integer")

    # rep() count parameter as variable
    class RepVarCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.count = HDL.Input(8)
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(s.count, s.in_)

    _check_error(RepVarCount(), r"rep\(\) count argument must be an integer")

    # rep() count parameter as expression with variable
    class RepExprCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.count = HDL.Input(8)
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(s.count + 1, s.in_)

    _check_error(RepExprCount(), r"rep\(\) count argument must be an integer")

    # rep() count parameter as constant expression
    class RepConstExprCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(b8(2) + 4, s.in_)

    _check_error(RepConstExprCount(), r"rep\(\) count argument .* integer")

    # rep() with negative count
    class RepNegIntCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(-1, s.in_)

    _check_error(RepNegIntCount(), r"count argument must be non-negative")

    # rep() with negative integer expression count
    class RepNegIntExprCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(1 - 2, s.in_)

    _check_error(RepNegIntExprCount(), r"count argument must be non-negative")

    # rep() with integer as a part
    class RepIntPart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(2, s.in_, 0xF)

    _check_error(RepIntPart(), r"Cannot replicate an integer constant")

    # rep() with integer expression as a part
    class RepIntExprPart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(4)
            s.out = HDL.Output(16)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= rep(2, s.in_, 0xA | 0xF)

    _check_error(RepIntExprPart(), r"Cannot replicate an integer constant")


def test_FunctionParser_Call_range_errors():
    # At LHS
    class RangeLHS(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):
            range(0, 10)[:] /= s.in_

    _check_error(RangeLHS(), r"range\(\) can only be used in a for loop")

    # Range only
    class RangeOnly(HDL.RawModule):
        @HDL.comb
        def update(s):  # pragma: no cover
            range(10)

    _check_error(RangeOnly(), r"range\(\) can only be used in a for loop")

    # Assign range
    class AssignRange(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= range(0, 10)

    _check_error(AssignRange(), r"range\(\) can only be used in a for loop")

    # Range in expression
    class RangeInExpr(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(4)

        @HDL.comb
        def update(s):  # pragma: no cover
            s.out /= range(0, 10) + 1

    _check_error(RangeInExpr(), r"range\(\) can only be used in a for loop")

    # No argument
    class NoArg(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range():
                s.out /= i

    _check_error(NoArg(), r"requires 1 to 3 arguments, got 0")

    # More than 3 arguments
    class MoreArgs(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0, 10, 1, 2):
                s.out /= i

    _check_error(MoreArgs(), r"requires 1 to 3 arguments, got 4")

    # Not integer start
    class NotIntStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(s.in_, 10):
                s.out /= i

    _check_error(NotIntStart(), r"lower bound must be an integer")

    # Negative start
    class NegStart(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(-1, 10):
                s.out /= i

    _check_error(NegStart(), r"lower bound must be non-negative")

    # Not integer stop
    class NotIntStop(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0, s.in_):
                s.out /= i

    _check_error(NotIntStop(), r"upper bound must be an integer")

    # Negative count
    class NegCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(-1):
                s.out /= i

    _check_error(NegCount(), r"count must be positive")

    # Zero count
    class ZeroCount(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0):
                s.out /= i

    _check_error(ZeroCount(), r"count must be positive")

    # Small stop
    class SmallStop(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(10, 9):
                s.out /= i

    _check_error(SmallStop(), r"upper bound must be greater than lower bound")

    # Same stop
    class SameStop(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(10, 10):
                s.out /= i

    _check_error(SameStop(), r"upper bound must be greater than lower bound")

    # Not integer step
    class NotIntStep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.in_ = HDL.Input(8)
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0, 10, s.in_):
                s.out /= i

    _check_error(NotIntStep(), r"step must be an integer")

    # Negative step
    class NegStep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0, 10, -1):
                s.out /= i

    _check_error(NegStep(), r"step must be positive")

    # Zero step
    class ZeroStep(HDL.RawModule):
        @HDL.build
        def build_all(s):
            s.out = HDL.Output(8)

        @HDL.comb
        def update(s):  # pragma: no cover
            for i in range(0, 10, 0):
                s.out /= i

    _check_error(ZeroStep(), r"step must be positive")


# Print all error messages by replacing _check_error
#
def _print_parsing_error(top: HDL.RawModule, error: str):
    tree = HDL.HDLStage()(top)
    tree_ir = StructurePass()(tree)
    try:
        BehaviorPass()(tree_ir)
    except HDLSyntaxError as e:
        print(e)


def print_FunctionParser_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_parsing_error
    test_FunctionParser_driving_errors()
    test_FunctionParser_port_connection_errors()
    test_FunctionParser_connection_errors()
    test_FunctionParser_comb_block_errors()
    test_FunctionParser_seq_block_errors()
    test_FunctionParser_seq_block_edge_errors()
    test_FunctionParser_nested_errors()
    test_FunctionParser_Assign_errors()
    test_FunctionParser_AugAssign_op_errors()
    test_FunctionParser_AugAssign_width_errors()
    test_FunctionParser_AugAssign_drive_errors()
    test_FunctionParser_Match_errors()
    test_FunctionParser_Match_pattern_errors()
    test_FunctionParser_Match_complete_errors()
    test_FunctionParser_For_errors()
    test_FunctionParser_For_i32_var_errors()
    test_FunctionParser_Constant_errors()
    test_FunctionParser_Name_errors()
    test_FunctionParser_Name_global_errors()
    test_FunctionParser_Name_global_i32_errors()
    test_FunctionParser_Attribute_errors()
    test_FunctionParser_Attribute_submodule_errors()
    test_FunctionParser_Attribute_bits_property_errors()
    test_FunctionParser_Attribute_bits_method_errors()
    test_FunctionParser_Attribute_array_errors()
    test_FunctionParser_Subscript_errors()
    test_FunctionParser_Subscript_array_errors()
    test_FunctionParser_Subscript_indexable_errors()
    test_FunctionParser_Subscript_slice_errors()
    test_FunctionParser_Subscript_part_select_errors()
    test_FunctionParser_Subscript_index_errors()
    test_FunctionParser_Subscript_index_const_expr_errors()
    test_FunctionParser_UnaryOp_errors()
    test_FunctionParser_BinOp_errors()
    test_FunctionParser_BinOp_pow_errors()
    test_FunctionParser_BinOp_shift_errors()
    test_FunctionParser_BoolOp_errors()
    test_FunctionParser_IfExp_errors()
    test_FunctionParser_Compare_errors()
    test_FunctionParser_Call_bits_errors()
    test_FunctionParser_Call_bits_ext_errors()
    test_FunctionParser_Call_Bool_errors()
    test_FunctionParser_Call_cat_errors()
    test_FunctionParser_Call_rep_errors()
    test_FunctionParser_Call_range_errors()
    _check_error = orig_check_error
