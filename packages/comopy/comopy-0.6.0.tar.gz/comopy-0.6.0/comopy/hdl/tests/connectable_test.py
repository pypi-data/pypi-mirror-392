# Tests for Connectable
#

import pytest

import comopy.testcases.ex_inherit as ex
from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.raw_module import RawModule, build
from comopy.hdl.signal import Input, Logic, Output
from comopy.hdl.signal_bundle import cat, rep
from comopy.utils import HDLAssemblyError


class Top(RawModule):
    @build
    def declare(s):
        s.in1 = Input(8)
        s.in2 = Input(4)
        s.in3 = Input(4)
        s.out1 = Output(8)
        s.out2 = Output(8)
        s.out3 = Output(4)
        s.logic1 = Logic(8)
        s.logic2 = Logic(4)
        s.logic3 = Logic(8)

    @build
    def connect(s):
        s.logic1 @= cat(s.in2, s.in3)  # concatenation
        s.logic2 @= s.in2 ^ s.in3  # expression
        s.logic3 @= cat(s.in1[2:6], s.in2[:2], s.in3[2:])  # read slice

    @build
    def connect_out(s):
        # fmt: off
        s.out1 @= (s.logic1  # multiple lines
                  & s.in1)  # noqa: E128
        # fmt: on
        s.out2[:4] @= s.logic2  # write slice
        s.out2[4:] @= rep(4, s.logic3[7], rep(0, s.logic2))  # overlapped
        cat(s.out3[:2], s.out3[2])[:] @= s.logic3[2:5]  # no overlap


def test_connect():
    top = Top()
    root = AssembleHDL()(top)
    assert top.logic1.data_driven == 0xFF
    assert top.logic2.data_driven == 0xF
    assert top.logic3.data_driven == 0xFF
    assert top.out1.data_driven == 0xFF
    assert top.out2.data_driven == 0xFF
    assert top.out3.data_driven == 0b0111  # Not all bits are driven
    conns = root._conn_blocks
    assert all(b.func.__name__ == "_connect_func" for b in conns)
    assert all(b.conn.func.__name__ == "_connect_func" for b in conns)
    assert conns[0].id == "[conn]s.logic1"
    assert conns[1].id == "[conn]s.logic2"
    assert conns[2].id == "[conn]s.logic3"
    assert conns[3].id == "[conn]s.out1"
    assert conns[4].id == "[conn]s.out2[:4]"
    assert conns[5].id == "[conn]s.out2[4:]"
    assert conns[6].id == "[conn]cat(s.out3[:2], s.out3[2])[:]"
    assert conns[0].conn.builder_name == "Top.connect"
    assert conns[1].conn.builder_name == "Top.connect"
    assert conns[2].conn.builder_name == "Top.connect"
    assert conns[3].conn.builder_name == "Top.connect_out"
    assert conns[4].conn.builder_name == "Top.connect_out"
    assert conns[5].conn.builder_name == "Top.connect_out"
    assert conns[6].conn.builder_name == "Top.connect_out"

    sig = Logic()
    with pytest.raises(RuntimeError, match=r"@= .* assembly-time API"):
        sig @= 0


def test_connect_inherit():
    calc = ex.CalcDebug()
    root = AssembleHDL()(calc)
    assert calc.get_builder_names() == [
        "ports",
        "input",
        "output",
        "result_xnor",
        "result_nor",
        "result",
        "debug_result",
    ]
    assert list(calc._func_info.keys()) == [
        "CalcInterface.input",
        "CalcInterface.output",
        "CalcUnit.result",
        "CalcDebug.debug_result",
    ]
    assert calc.get_builders() == (
        ex.CalcInterface.ports,
        ex.CalcInterface.input,
        ex.CalcInterface.output,
        ex.XnorImpl.result_xnor,  # from right to left
        ex.NorImpl.result_nor,
        ex.CalcUnit.result,
        ex.CalcDebug.debug_result,
    )
    assert calc.a.data_driven == 0xFF
    assert calc.b.data_driven == 0xFF
    assert calc.res.data_driven == 0xFF
    assert calc.out.data_driven == 0xFF
    assert calc.debug.data_driven == 0xFF
    # in comb
    assert calc.nor.data_driven == 0
    assert calc.xnor.data_driven == 0
    conns = root._conn_blocks
    assert len(conns) == 5
    assert all(b.func.__name__ == "_connect_func" for b in conns)
    assert all(b.conn.func.__name__ == "_connect_func" for b in conns)
    assert conns[0].conn.builder_name == "CalcInterface.input"  # a
    assert conns[1].conn.builder_name == "CalcInterface.input"  # b
    assert conns[2].conn.builder_name == "CalcInterface.output"  # out
    assert conns[3].conn.builder_name == "CalcUnit.result"  # res
    assert conns[4].conn.builder_name == "CalcDebug.debug_result"  # debug


def test_connect_override():
    calc = ex.Inject()
    root = AssembleHDL()(calc)
    assert calc.get_builder_names() == [
        "ports",
        "input",
        "output",
        "result_xnor",
        "result_nor",
        "result",
        "debug_result",
    ]
    assert list(calc._func_info.keys()) == [
        "Inject.input",
        "CalcInterface.output",
        "CalcUnit.result",
        "CalcDebug.debug_result",
    ]
    assert calc.get_builders() == (
        ex.CalcInterface.ports,
        ex.Inject.input,
        ex.CalcInterface.output,
        ex.XnorImpl.result_xnor,  # from right to left
        ex.NorImpl.result_nor,
        ex.CalcUnit.result,
        ex.CalcDebug.debug_result,
    )
    conns = root._conn_blocks
    assert len(conns) == 5
    assert all(b.func.__name__ == "_connect_func" for b in conns)
    assert all(b.conn.func.__name__ == "_connect_func" for b in conns)
    assert conns[0].conn.builder_name == "Inject.input"  # a
    assert conns[1].conn.builder_name == "Inject.input"  # b
    assert conns[2].conn.builder_name == "CalcInterface.output"  # out
    assert conns[3].conn.builder_name == "CalcUnit.result"  # res
    assert conns[4].conn.builder_name == "CalcDebug.debug_result"  # debug


def test_connect_override_call_super():
    calc = ex.Inject2()
    circuit = AssembleHDL()(calc)
    assert calc.get_builder_names() == [
        "ports",
        "input",
        "output",
        "result_xnor",
        "result_nor",
        "result",
        "debug_result",
    ]
    assert list(calc._func_info.keys()) == [
        "Inject2.input",
        "CalcInterface.input",
        "CalcInterface.output",
        "CalcUnit.result",
        "CalcDebug.debug_result",
    ]
    assert calc.get_builders() == (
        ex.CalcInterface.ports,
        ex.Inject2.input,
        ex.CalcInterface.output,
        ex.XnorImpl.result_xnor,  # from right to left
        ex.NorImpl.result_nor,
        ex.CalcUnit.result,
        ex.CalcDebug.debug_result,
    )
    conns = circuit._conn_blocks
    assert len(conns) == 7
    assert all(b.func.__name__ == "_connect_func" for b in conns)
    assert all(b.conn.func.__name__ == "_connect_func" for b in conns)
    assert conns[0].conn.builder_name == "CalcInterface.input"  # a
    assert conns[1].conn.builder_name == "CalcInterface.input"  # b
    assert conns[2].conn.builder_name == "Inject2.input"  # inject_a
    assert conns[3].conn.builder_name == "Inject2.input"  # inject_b
    assert conns[4].conn.builder_name == "CalcInterface.output"  # out
    assert conns[5].conn.builder_name == "CalcUnit.result"  # res
    assert conns[6].conn.builder_name == "CalcDebug.debug_result"  # debug


def _check_error(top: RawModule, error: str):
    with pytest.raises(HDLAssemblyError, match=error):
        AssembleHDL()(top)


def test_connect_assign_errors():
    # Bad assignment
    class BadAssign1(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out /= 0

    _check_error(BadAssign1(), r"simulation-time API")

    class BadAssign2(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out <<= 0

    _check_error(BadAssign2(), r"simulation-time API")

    # Mismatched widths for assignment
    class MismatchAssign(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(4)
            s.out @= s.in1

    _check_error(MismatchAssign(), r"mismatch for assignment")


def test_connect_driver_errors():
    # Multiple drivers
    class MultiDriver(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.logic = Logic(8)
            s.logic @= s.in1
            s.out @= s.logic
            s.out @= s.in1

    _check_error(MultiDriver(), r"Multiple drivers are not allowed")

    # Overlapped drivers
    class OverlapDriver(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out[:5] @= s.in1[:5]
            s.out[4:] @= s.in1[4:]

    _check_error(OverlapDriver(), r"Multiple drivers are not allowed")


def test_connect_bundle_errors():
    # Bundle driven
    class BundleDriven(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            cat(s.out[:4], s.out[4:])[:] @= s.in1
            s.out @= s.in1

    _check_error(BundleDriven(), r"Multiple drivers are not allowed")

    # Overlapped bundle
    class OverlapBundle(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            cat(s.out[:4], s.out[2:])[:] @= cat(rep(2, s.in1[7]), s.in1)

    _check_error(OverlapBundle(), r"immutable Bits10")

    # Immutable bundle
    class ImmutableBundle(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            rep(2, s.out)[:] @= rep(2, s.in1)

    _check_error(ImmutableBundle(), r"immutable Bits16")

    # Empty bundle
    class EmptyBundle(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            rep(0, s.out)[:] @= s.in1

    _check_error(EmptyBundle(), r"Cannot directly access an empty")


def test_connect_builder_errors():
    # Call another builder
    class CallBuilder(RawModule):
        @build
        def declare(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.connect_out()

        @build
        def connect_out(s):
            s.out @= s.in1

    _check_error(CallBuilder(), r"Multiple drivers are not allowed")

    # Two connections in one line
    class TwoConn(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            # fmt: off
            s.out @= s.in1; s.out @= s.in1  # noqa: E702
            # fmt: on

    _check_error(TwoConn(), r"Only one '@=' .* is allowed")

    # Not builder
    class NotBuilder(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.connect()

        def connect(s):
            s.out @= s.in1

    _check_error(NotBuilder(), r"only supported in builder methods")


def test_connect_func_errors():
    # ext() width
    class ExtVarWidth(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out @= s.in1.ext(s.in1)

    _check_error(ExtVarWidth(), r"ext\(\) argument must be an integer")

    # ext() small width
    class ExtSmallWidth(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out @= s.in1.ext(1)

    _check_error(ExtSmallWidth(), r"must be greater than the current width 8")

    # ext() negative width
    class ExtNegWidth(RawModule):
        @build
        def connect(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.out @= s.in1.ext(-1)

    _check_error(ExtNegWidth(), r"must be greater than the current width 8")


# Print all error messages by replacing _check_error
#
def _print_assembly_error(top: RawModule, error: str):
    try:
        AssembleHDL()(top)
    except HDLAssemblyError as e:
        print(e)


def print_Connectable_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_assembly_error
    test_connect_assign_errors()
    test_connect_driver_errors()
    test_connect_bundle_errors()
    test_connect_builder_errors()
    test_connect_func_errors()
    _check_error = orig_check_error
