# Tests for HDLStage
#

import pytest

from comopy.hdl.circuit_node import CircuitNode
from comopy.hdl.hdl_stage import HDLStage
from comopy.hdl.raw_module import RawModule


def test_HDLStage():
    m = RawModule(name="Top")
    assert not m.assembled
    tree = HDLStage()(m)
    assert m.assembled
    assert not m.simulating
    assert isinstance(tree, CircuitNode)
    assert tree.obj is m
    assert tree.owner is None
    assert tree.elements == ()
    assert tree.level == 0
    assert tree.name == "Top"
    assert tree.full_name == "Top"
    assert tree.top is tree
    assert tree.comb_blocks == ()
    assert tree.seq_blocks == ()
    assert tree.is_root
    assert tree.is_assembled_module

    s = HDLStage()
    with pytest.raises(TypeError, match="expects an HDL module or package"):
        s(1)
