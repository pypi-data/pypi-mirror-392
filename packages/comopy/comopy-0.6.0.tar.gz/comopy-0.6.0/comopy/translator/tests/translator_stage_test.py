# Tests for TranslatorStage
#

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage, IRStage
from comopy.translator.translator_stage import TranslatorStage


def test_TranslatorStage():
    top = ex.Wire1()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    tree_trans = TranslatorStage()(tree_ir)
    assert tree_trans is tree_ir
    trans = top.translator
    sv = trans.emit()
    assert sv.find("\n    __out_bits = in_;\n") > 0


def test_TranslatorStage_error():
    s = TranslatorStage()
    with pytest.raises(TypeError, match="input must be an HDL.CircuitNode"):
        s(1)

    tree = HDLStage()(ex.Wire1())
    with pytest.raises(ValueError, match="input must be the root"):
        s(tree.elements[0])

    tree = HDLStage()(ex.Wire4())
    with pytest.raises(ValueError, match="has not been .* IR stage"):
        s(tree)
