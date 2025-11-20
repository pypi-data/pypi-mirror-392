# Tests for IRStage
#

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage
from comopy.ir.ir_stage import IRStage


def test_IRStage_error():
    s = IRStage()
    with pytest.raises(TypeError, match="input must be an HDL.CircuitNode"):
        s(1)

    tree = HDLStage()(ex.Wire1())
    with pytest.raises(ValueError, match="input must be the root"):
        s(tree.elements[0])
