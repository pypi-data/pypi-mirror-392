# Tests for RawModule
#

import pytest

from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.raw_module import RawModule, build, comb, seq
from comopy.hdl.signal import Input, Output
from comopy.utils import HDLAssemblyError


def test_RawModule_func_info():
    class Sub(RawModule):
        ...

    class Top(RawModule):
        sub1 = Sub()
        sub2 = Sub()

    assert Top._func_info is not RawModule._func_info
    assert Sub._func_info is not RawModule._func_info
    assert Top._func_info is not Sub._func_info

    top = Top()
    assert top.get_func_info_by_name("update1") is None
    # cache info
    top._func_info["update1"] = 1
    top._func_info["update2"] = 2
    assert len(top._func_info) == 2
    assert top.get_func_info_by_name("update1") == 1
    assert top.get_func_info_by_name("update2") == 2
    # no cache entry
    assert top.get_func_info_by_name("update3") is None
    # update
    top._func_info["update1"] = 3
    assert len(top._func_info) == 2
    assert top.get_func_info_by_name("update1") == 3
    # no cache entry
    assert top.sub1.get_func_info_by_name("update") is None
    # cached in class, not in instance
    top.sub1._func_info["update"] = "sub1"
    assert len(top.sub1._func_info) == 1
    assert len(top.sub2._func_info) == 1
    assert top.sub1.get_func_info_by_name("update") == "sub1"
    assert top.sub2.get_func_info_by_name("update") == "sub1"
    top.sub2._func_info["update"] = "sub2"
    assert len(top.sub1._func_info) == 1
    assert len(top.sub2._func_info) == 1
    assert top.sub1.get_func_info_by_name("update") == "sub2"
    assert top.sub2.get_func_info_by_name("update") == "sub2"
    # cached in subclass, not in base class Module
    assert len(top._func_info) == 2

    class NewTop(Top):
        ...

    new_top = NewTop()
    assert new_top._func_info is not top._func_info
    assert new_top.get_func_info_by_name("update1") is None
    assert len(top._func_info) == 2
    assert len(new_top._func_info) == 0
    new_top._func_info["update1"] = 4
    assert top.get_func_info_by_name("update1") == 3
    assert new_top.get_func_info_by_name("update1") == 4


def test_RawModule_properties():
    module = RawModule()
    assert module.assembled is False
    assert module.simulating is False
    assert module.is_module is True
    assert module.is_package is False
    assert module.is_port is False
    assert module.ir is None
    assert module.simulator is None
    assert module.translator is None
    assert module.vsimulator is None


class Outer(RawModule):
    @build
    def build_all(s):  # pragma: no cover
        ...

    @comb
    def update(s):  # pragma: no cover
        ...

    @seq
    def update_ff(s):  # pragma: no cover
        ...


def test_RawModule_builders():
    assert Outer._tags == ("build", "comb", "seq")
    assert Outer._tagged_methods == {}
    assert Outer._tagged_methods is not RawModule._tagged_methods
    assert Outer._bound_methods == {}
    assert Outer._bound_methods is not RawModule._bound_methods

    assert Outer.get_tagged_methods("build") == ()
    outer1 = Outer()
    outer2 = Outer()
    outer1.init_tagged_methods()
    assert Outer.get_builders() == (Outer.build_all,)
    assert outer1.get_builders() == (Outer.build_all,)
    assert outer2.get_builders() == (Outer.build_all,)
    outer2.init_tagged_methods()
    assert outer1.get_builders() == (Outer.build_all,)
    assert outer2.get_builders() == (Outer.build_all,)
    assert Outer.get_builder_names() == ["build_all"]

    class Common(Outer):
        @build
        def build_common(s):  # pragma: no cover
            ...

    class Inner(Common):
        @build
        def build_ports(s):  # pragma: no cover
            ...

        @build
        def build_connections(s):  # pragma: no cover
            ...

    assert Outer.get_builders() == (Outer.build_all,)
    assert Common.get_builders() == ()
    assert Inner.get_builders() == ()
    inner1 = Inner()
    inner2 = Inner()
    inner1.init_tagged_methods()
    assert inner1.get_builder_names() == [
        "build_all",
        "build_common",
        "build_ports",
        "build_connections",
    ]
    assert inner2.get_builder_names() == inner1.get_builder_names()
    inner2.init_tagged_methods()
    assert inner1.get_builder_names() == [
        "build_all",
        "build_common",
        "build_ports",
        "build_connections",
    ]
    assert inner2.get_builder_names() == inner1.get_builder_names()

    # No builder
    class NoBuilder(RawModule):
        ...

    assert NoBuilder.get_builders() == ()
    no_builder = NoBuilder()
    no_builder.init_tagged_methods()
    assert NoBuilder.get_builders() == ()
    assert no_builder.get_builder_names() == []


def test_RawModule_comb_blocks():
    outer = Outer()
    outer.init_tagged_methods()
    combs = outer.get_comb_blocks()
    assert combs == (Outer.update,)

    class Common(Outer):
        # override Outer.update()
        @comb
        def update(s):  # pragma: no cover
            ...

    class Inner(Common):
        @comb
        def update1(s):  # pragma: no cover
            ...

        @comb
        def update2(s):  # pragma: no cover
            ...

    # Not assembled
    assert Common.get_comb_blocks() == ()
    assert Inner.get_comb_blocks() == ()

    inner = Inner()
    assert not inner.assembled
    inner._assemble()
    assert inner.assembled
    assert Common.get_comb_blocks() == (Common.update,)
    assert Inner.get_comb_blocks() == (
        Common.update,
        Inner.update1,
        Inner.update2,
    )
    assert len(inner.get_comb_blocks()) == 3


def test_RawModule_seq_blocks():
    outer = Outer()
    outer.init_tagged_methods()
    seqs = outer.get_seq_blocks()
    assert seqs == (Outer.update_ff,)

    class Common(Outer):
        # override Outer.update_ff()
        @seq
        def update_ff(s):  # pragma: no cover
            ...

    class Inner(Common):
        @seq
        def update1_ff(s):  # pragma: no cover
            ...

        @seq
        def update2_ff(s):  # pragma: no cover
            ...

    # Not assembled
    assert Common.get_seq_blocks() == ()
    assert Inner.get_seq_blocks() == ()

    inner = Inner()
    assert not inner.assembled
    inner._assemble()
    assert inner.assembled
    assert Common.get_seq_blocks() == (Common.update_ff,)
    assert Inner.get_seq_blocks() == (
        Common.update_ff,
        Inner.update1_ff,
        Inner.update2_ff,
    )
    assert len(inner.get_seq_blocks()) == 3


def test_RawModule_submodule():
    class Sub(RawModule):
        @build
        def build_all(s):
            s.a = Input(8)
            s.b = Input(8)
            s.x = Output(8)
            s.x @= s.a ^ s.b

    # Connect all by order
    class AllOrdered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, s.in2, s.out)

    top = AllOrdered()
    tree = AssembleHDL()(top)
    assert len(tree.inst_blocks) == 1
    assert tree.inst_blocks[0].id == "[inst]sub"
    assert len(tree.conn_blocks) == 3
    assert top.sub.port_conns == [top.in1, top.in2, top.out]

    # Connect partial by order
    class PartialOrdered(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, s.in2)

    top = PartialOrdered()
    tree = AssembleHDL()(top)
    assert len(tree.inst_blocks) == 1
    assert tree.inst_blocks[0].id == "[inst]sub"
    assert len(tree.conn_blocks) == 2
    assert top.sub.port_conns == [top.in1, top.in2, None]

    # Connect all by name
    class AllNamed(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(a=s.in1, b=s.in2, x=s.out)

    top = AllNamed()
    tree = AssembleHDL()(top)
    assert len(tree.inst_blocks) == 1
    assert tree.inst_blocks[0].id == "[inst]sub"
    assert len(tree.conn_blocks) == 3
    assert top.sub.port_conns == [top.in1, top.in2, top.out]

    # Connect partial by name
    class PartialNamed(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(a=s.in1, x=s.out)

    top = PartialNamed()
    tree = AssembleHDL()(top)
    assert len(tree.inst_blocks) == 1
    assert tree.inst_blocks[0].id == "[inst]sub"
    assert len(tree.conn_blocks) == 2
    assert top.sub.port_conns == [top.in1, None, top.out]


def _check_error(top: RawModule, error: str):
    with pytest.raises(HDLAssemblyError, match=error):
        AssembleHDL()(top)


def test_RawModule_tagged_errors():
    # Conflict with reserved method names
    with pytest.raises(NameError, match=r"conflicts with a reserved name"):

        class ReservedMethod1(RawModule):
            @build
            def assemble(s):  # pragma: no cover
                ...

    with pytest.raises(NameError, match=r"conflicts with a reserved name"):

        class ReservedMethod2(RawModule):
            @comb
            def assemble_connection(s):  # pragma: no cover
                ...

    # Conflict with TaggedClass names
    with pytest.raises(NameError, match=r"conflicts with a TaggedClass attr"):

        class TaggedAttrName(RawModule):
            @seq
            def _tags(s):  # pragma: no cover
                ...

    with pytest.raises(NameError, match=r"conflicts with a TaggedClass attr"):

        class TaggedMethodName(RawModule):
            @build
            def init_tagged_methods(s):  # pragma: no cover
                ...

    # Class as builder
    class ClassBuilder(RawModule):
        @build
        class builder:
            def __call__():  # pragma: no cover
                ...

    _check_error(ClassBuilder(), r"Tagged .* is not a function.")

    # Re-define the module
    class Redefined(RawModule):
        @build
        def build_ports(s):  # pragma: no cover
            ...

    class Redefined(RawModule):  # noqa: F811
        @build
        def build_ports(s):  # pragma: no cover
            ...

    _check_error(Redefined(), r"Tagged .* is not current")

    # Re-define the module
    class Redefined(RawModule):
        @build
        def build_all(s):  # pragma: no cover
            ...

    _check_error(Redefined(), r"Tagged .* is not found")

    # Duplicate comb block
    class DupBlock(RawModule):
        @comb
        def update(s):  # pragma: no cover
            ...

        @comb
        def update(s):  # noqa: F811
            ...  # pragma: no cover

    _check_error(DupBlock(), r"Tagged .* is not current")

    # Conflict with RawModule names
    class PropertyName(RawModule):
        @build
        def all_ports(s):  # pragma: no cover
            ...

    _check_error(PropertyName(), r"PropertyName cannot override .* all_ports")

    class ClassAttr(RawModule):
        @build
        def _auto_ports(s):  # pragma: no cover
            ...

    _check_error(ClassAttr(), r"ClassAttr cannot override .* _auto_ports")

    class AttrName(RawModule):
        @comb
        def _simulator(s):  # pragma: no cover
            ...

    _check_error(AttrName(), r"AttrName cannot override .* _simulator")

    class ClassMethod(RawModule):
        @seq
        def get_comb_blocks(s):  # pragma: no cover
            ...

    _check_error(ClassMethod(), r"ClassMethod cannot .* get_comb_blocks")

    class MethodName(RawModule):
        @build
        def connect_submodule(s):  # pragma: no cover
            ...

    _check_error(MethodName(), r"MethodName cannot .* connect_submodule")

    class ConnBuilder(RawModule):
        @build
        def _connect_submodule_port(s):  # pragma: no cover
            ...

    _check_error(ConnBuilder(), r"ConnBuilder .* _connect_submodule_port")


def test_RawModule_auto_port_errors():
    class DupAutoPorts(RawModule):
        _auto_pos_edges = ("clk",)
        _auto_neg_edges = ("rst_n",)
        _auto_ports = ("enable", "clk", "rst_n")

    _check_error(DupAutoPorts(), r"Duplicated .* DupAutoPorts: clk, rst_n")


def test_RawModule_port_errors():
    class RedirectPort(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.out = Output(8)
            s.in2 = Input(8).input()

    _check_error(RedirectPort(), r"Cannot change signal direction")


def test_RawModule_connect_errors():
    class Sub(RawModule):
        @build
        def build_all(s):
            s.a = Input(8)
            s.b = Input(8)
            s.x = Output(8)
            s.x @= s.a ^ s.b

    # More ports by order
    class TooManyArgs(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, s.in2, s.out, s.out)

    _check_error(TooManyArgs(), r"Sub\(\) expects 3 port .* got 4")

    # Bad port name
    class BadPortName(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(a=s.in1, b=s.in2, y=s.out)

    _check_error(BadPortName(), r"Invalid port name 'y' in Sub\(\)")

    # Mixed ordered and named connections
    class MixedConns(RawModule):
        @build
        def build_all(s):
            s.in1 = Input(8)
            s.in2 = Input(8)
            s.out = Output(8)
            s.sub = Sub(s.in1, b=s.in2, x=s.out)

    _check_error(MixedConns(), r"Sub\(\) cannot mix ordered and named")


# Print all error messages by replacing _check_error
#
def _print_assembly_error(top: RawModule, error: str):
    try:
        AssembleHDL()(top)
    except HDLAssemblyError as e:
        print(e)


def print_RawModule_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_assembly_error
    test_RawModule_tagged_errors()
    test_RawModule_auto_port_errors()
    test_RawModule_port_errors()
    test_RawModule_connect_errors()
    _check_error = orig_check_error
