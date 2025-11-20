# Tests for Module
#

import pytest

from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.module import Module
from comopy.hdl.raw_module import RawModule, build
from comopy.hdl.signal import Input, Output, Wire
from comopy.utils import HDLAssemblyError


def test_Module():
    class Sub(Module):
        ...

    class Top(Module):
        @build
        def build_all(s):
            s.sub = Sub()

    top = Top()
    AssembleHDL()(top)
    assert isinstance(top.clk, Wire) and top.clk.is_scalar_input
    assert len(top._ports) == 1
    assert top._ports[0].name == "clk"
    assert top._port_conns == [None]
    assert isinstance(top.sub.clk, Wire) and top.sub.clk.is_scalar_input
    assert len(top.sub._ports) == 1
    assert top.sub._ports[0].name == "clk"
    assert top.sub._port_conns[0] is top.clk

    # Raw top
    class RawTop(RawModule):
        @build
        def build_all(s):
            s.sub = Sub()

    top = RawTop()
    AssembleHDL()(top)
    assert not hasattr(top, "clk")
    assert isinstance(top.sub.clk, Wire) and top.sub.clk.is_scalar_input
    assert len(top.sub._ports) == 1
    assert top.sub._ports[0].name == "clk"
    assert top.sub._port_conns == [None]

    # Raw sub
    class RawSub(RawModule):
        @build
        def build_all(s):
            s.clk = Input()
            s.reset = Input()

    class ModuleTop(Module):
        @build
        def build_all(s):
            s.sub = RawSub()

    top = ModuleTop()
    AssembleHDL()(top)
    assert isinstance(top.clk, Wire) and top.clk.is_scalar_input
    assert len(top._ports) == 1
    assert top._ports[0].name == "clk"
    assert top._port_conns == [None]
    assert isinstance(top.sub.clk, Wire) and top.sub.clk.is_scalar_input
    assert isinstance(top.sub.reset, Wire) and top.sub.reset.is_scalar_input
    assert len(top.sub._ports) == 2
    assert top.sub._ports[0].name == "clk"
    assert top.sub._ports[1].name == "reset"
    assert top.sub._port_conns == [None, None]


def test_Module_submodule():
    class Sub(Module):
        @build
        def build_all(s):
            s.a = Input(8)
            s.b = Input(8)
            s.x = Output(8)
            s.x @= s.a ^ s.b

    # Connect all by order
    class OrderedAll(Module):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, s.in2, s.out)

    top = OrderedAll()
    tree = AssembleHDL()(top)
    assert len(tree.conn_blocks) == 4
    assert top.sub._port_conns[0] is top.clk
    assert top.sub._port_conns[1] is top.in1
    assert top.sub._port_conns[2] is top.in2
    assert top.sub._port_conns[3] is top.out

    # Connect partial by order
    class OrderedPartial(Module):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, s.in2)

    top = OrderedPartial()
    tree = AssembleHDL()(top)
    assert len(tree.conn_blocks) == 3
    assert top.sub._port_conns[0] is top.clk
    assert top.sub._port_conns[1] is top.in1
    assert top.sub._port_conns[2] is top.in2
    assert top.sub._port_conns[3] is None


def _check_error(top: RawModule, error: str):
    with pytest.raises(HDLAssemblyError, match=error):
        AssembleHDL()(top)


def test_Module_errors():
    # Redefined clock signal
    class RedefineClock(Module):
        @build
        def build_sub(s):
            s.clk = Input()

    _check_error(RedefineClock(), r"Cannot overwrite attribute 'clk'")

    # Manually connect clock signal
    class Sub(Module):
        ...

    class ReconnectClock(Module):
        @build
        def build_all(s):
            s.sub = Sub(clk=s.clk)

    _check_error(ReconnectClock(), r"Port 'clk' has been auto-connected")


# Print all error messages by replacing _check_error
#
def _print_assembly_error(top: RawModule, error: str):
    try:
        AssembleHDL()(top)
    except HDLAssemblyError as e:
        print(e)


def print_Module_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_assembly_error
    test_Module_errors()
    _check_error = orig_check_error
