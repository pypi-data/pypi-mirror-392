# Tests for AssembleHDL
#

import pytest

from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.circuit_node import Behavior, CircuitNode
from comopy.hdl.circuit_object import CircuitObject
from comopy.hdl.package import Package
from comopy.hdl.raw_module import RawModule, build, comb, seq
from comopy.hdl.signal import Logic
from comopy.utils import HDLAssemblyError


def test_AssembleHDL_assemble():
    # Simple root
    top = CircuitObject(name="top")
    assert not top.assembled
    tree = AssembleHDL()(top)
    assert not AssembleHDL.is_assembling()
    assert top.assembled
    assert isinstance(tree, CircuitNode)
    assert tree.is_root
    assert tree.obj == top
    assert tree.owner is None
    assert tree.level == 0
    assert tree.top == tree

    # Builders & behaviors
    class Top(RawModule):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.child = CircuitObject()

        @build
        def build_ports(self):
            self.port1 = CircuitObject()

        @build
        def build_logics(self):
            self.logic1 = CircuitObject()

        @comb
        def update1(self):  # pragma: no cover
            ...

        @comb
        def update2(self):  # pragma: no cover
            ...

        @seq
        def update_ff(self):  # pragma: no cover
            ...

    top = Top(name="top")
    assert not top.assembled
    assembler = AssembleHDL()
    assert not AssembleHDL.is_assembling()
    tree = assembler(top)
    assert not AssembleHDL.is_assembling()
    assert top.assembled
    assert isinstance(tree, CircuitNode)
    assert tree.is_root
    assert tree.obj == top
    assert not top.child.assembled  # No builder for child
    assert hasattr(top, "port1")
    assert top.port1.assembled
    assert top.port1.name == "port1"
    assert hasattr(top, "logic1")
    assert top.logic1.assembled
    assert top.logic1.name == "logic1"
    port1 = tree.elements[0]
    assert port1.obj == top.port1
    assert port1.owner == tree
    assert port1.level == 1
    assert port1.name == "port1"
    assert port1.full_name == "top.port1"
    assert port1.top == tree
    assert not port1.is_root
    logic1 = tree.elements[1]
    assert logic1.obj == top.logic1
    assert logic1.owner == tree
    assert logic1.level == 1
    assert logic1.name == "logic1"
    assert logic1.full_name == "top.logic1"
    assert logic1.top == tree
    assert not logic1.is_root
    assert len(tree.comb_blocks) == 2
    assert tree.comb_blocks[0].func == Top.update1
    assert tree.comb_blocks[0].id == "[comb]update1"
    assert tree.comb_blocks[0].kind == Behavior.Kind.COMB_BLOCK
    assert tree.comb_blocks[0].deps.reads == set()
    assert tree.comb_blocks[0].deps.writes == set()
    assert tree.comb_blocks[1].func == Top.update2
    assert tree.comb_blocks[1].id == "[comb]update2"
    assert tree.comb_blocks[1].kind == Behavior.Kind.COMB_BLOCK
    assert tree.comb_blocks[1].deps.reads == set()
    assert tree.comb_blocks[1].deps.writes == set()
    assert len(tree.seq_blocks) == 1
    assert tree.seq_blocks[0].func == Top.update_ff
    assert tree.seq_blocks[0].id == "[seq]update_ff"
    assert tree.seq_blocks[0].kind == Behavior.Kind.SEQ_BLOCK
    assert tree.seq_blocks[0].deps.reads == set()
    assert tree.seq_blocks[0].deps.writes == set()


def test_AssembleHDL_assemble_subclass():
    class Common(RawModule):
        @build
        def build_common(self):
            self.port1 = CircuitObject()

        @comb
        def update(self):  # pragma: no cover
            ...

        @seq
        def update_ff(self):  # pragma: no cover
            ...

    class Top(Common):
        @build
        def build_all(self):
            self.port2 = CircuitObject()

        @comb
        def update(self):  # pragma: no cover
            ...

        @seq
        def update_ff(self):  # pragma: no cover
            ...

    top = Top(name="Top")
    tree = AssembleHDL()(top)
    assert isinstance(tree, CircuitNode)
    assert tree.is_root
    assert hasattr(top, "build_all")
    assert hasattr(top, "build_common")
    assert hasattr(top, "port1")
    assert top.port1.assembled
    assert top.port1.name == "port1"
    assert top.port2.assembled
    assert top.port2.name == "port2"
    # base class builder first
    port1 = tree.elements[0]
    port2 = tree.elements[1]
    assert port1.obj == top.port1
    assert port1.owner == tree
    assert port1.level == 1
    assert port1.full_name == "Top.port1"
    assert port2.obj == top.port2
    assert port2.owner == tree
    assert port2.level == 1
    assert port2.full_name == "Top.port2"
    assert len(tree.comb_blocks) == 1
    assert tree.comb_blocks[0].func == Top.update
    assert tree.comb_blocks[0].id == "[comb]update"
    assert tree.comb_blocks[0].kind == Behavior.Kind.COMB_BLOCK
    assert tree.comb_blocks[0].deps.reads == set()
    assert tree.comb_blocks[0].deps.writes == set()
    assert len(tree.seq_blocks) == 1
    assert tree.seq_blocks[0].func == Top.update_ff
    assert tree.seq_blocks[0].id == "[seq]update_ff"
    assert tree.seq_blocks[0].kind == Behavior.Kind.SEQ_BLOCK
    assert tree.seq_blocks[0].deps.reads == set()
    assert tree.seq_blocks[0].deps.writes == set()

    # TODO More tests for inheritance
    # - MRO
    # - None-Module base class
    # - Conflicts
    # - Override a builder?


def _check_error(top: RawModule | Package, error: str):
    with pytest.raises(HDLAssemblyError, match=error):
        AssembleHDL()(top)
    assert not AssembleHDL.is_assembling()


def test_AssembleHDL_errors():
    # Rebuild top
    class Rebuild(RawModule):
        @build
        def build_all(self):
            ...

    top = Rebuild()
    AssembleHDL()(top)
    _check_error(top, r"has already been assembled")

    # Reassign
    class Reassign(RawModule):
        @build
        def construct(self):
            self.child = CircuitObject()
            self.child = CircuitObject()

    # Also checks the builder name in the error string.
    _check_error(Reassign(), r"construct.*\n.*\n.*overwrite attribute 'child'")

    # Reassign in another builder
    class ReassignBuilder(RawModule):
        @build
        def build_child(self):
            self.child = CircuitObject()

        @build
        def reassign(self):
            self.child = CircuitObject()

    _check_error(ReassignBuilder(), r"overwrite attribute 'child'")

    # Reassign non-circuit
    class ReassignNotCircuit(RawModule):
        @build
        def build_all(self):
            self.child = CircuitObject()
            self.child = 1

    _check_error(ReassignNotCircuit(), r"overwrite attribute 'child'")

    # Call another builder
    class CallBuilder(RawModule):
        @build
        def build_child(self):
            self.child = CircuitObject()

        @build
        def build_all(self):
            self.build_child()

    _check_error(CallBuilder(), r"overwrite attribute 'child'")

    # Overwrite a function
    class OverwriteFunc(RawModule):
        @build
        def build_all(self):
            self.assemble = Logic()

    _check_error(OverwriteFunc(), r"overwrite callable attribute 'assemble'")

    # Rebuild a child
    class RebuildChild(RawModule):
        def __init__(self, out_obj: CircuitObject):
            super().__init__()
            self.out_obj = out_obj

        @build
        def build_all(self):
            self.child = self.out_obj

    obj = CircuitObject(name="out_obj")
    AssembleHDL()(obj)
    _check_error(RebuildChild(out_obj=obj), r"has already been assembled")

    # Alias across builders
    class Alias(RawModule):
        @build
        def build_all(self):
            self.child = CircuitObject()

        @build
        def alias(self):
            self.child1 = self.child

    _check_error(Alias(), r"has already been assembled")


def test_AssembleHDL_submodule_errors():
    class SubReassign(RawModule):
        @build
        def build_sub(self):
            self.child = CircuitObject()
            self.child = CircuitObject()

    class Top(RawModule):
        @build
        def build_all(self):
            self.sub = SubReassign()

    # Check builder position
    _check_error(Top(), r"in build_sub\(\)")


# Print all error messages by replacing _check_error
#
def _print_assembly_error(top: RawModule | Package, error: str):
    try:
        AssembleHDL()(top)
    except HDLAssemblyError as e:
        print(e)


def print_AssembleHDL_errors():
    global _check_error
    orig_check_error = _check_error
    _check_error = _print_assembly_error
    test_AssembleHDL_errors()
    test_AssembleHDL_submodule_errors()
    _check_error = orig_check_error
