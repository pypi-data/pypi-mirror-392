# Tests for LocalParam
#

import pytest

from comopy.datatypes import Bits, ParamConst
from comopy.hdl.assemble_hdl import AssembleHDL
from comopy.hdl.circuit_object import CircuitObject
from comopy.hdl.parameter import LocalParam
from comopy.hdl.raw_module import RawModule, build
from comopy.hdl.signal import Signal


def test_LocalParam_init():
    LP1 = LocalParam(8)
    assert isinstance(LP1, ParamConst)
    assert isinstance(LP1.param_value, int)
    assert LP1.param_name == ""
    assert LP1.param_value == 8
    assert LP1.is_literal
    assert not LP1.is_expr
    LP1.param_name = "LP"
    assert LP1.param_name == "LP"
    assert not LP1.is_literal
    assert isinstance(LP1, CircuitObject)
    assert LP1.name == "_Unknown_"
    assert not LP1.assembled
    assert not LP1.simulating
    assert not LP1.is_module
    assert not LP1.is_package
    assert LP1.direction is None
    assert not LP1.is_input_port
    assert not LP1.is_output_port
    assert not LP1.is_port
    assert not LP1.is_scalar_input

    LP1.pkg_name = "pkg"
    assert LP1.pkg_name == "pkg"

    LP2 = LocalParam(LP1 * 2)
    assert isinstance(LP2, LocalParam)
    assert isinstance(LP2.param_value, int)
    assert LP2.param_name == ""
    assert LP2.param_value == 16
    assert not LP2.is_literal
    assert LP2.is_expr
    assert LP2.op == ParamConst.Op.MUL
    assert LP2.left is LP1
    assert isinstance(LP2.right, int) and LP2.right == 2
    assert isinstance(LP2, CircuitObject)

    with pytest.raises(ValueError, match=r"Invalid expression for LocalParam"):
        LocalParam(LP1 + LP2 - 8.0)
    with pytest.raises(TypeError, match=r"Invalid data type for LocalParam"):
        LocalParam(8.0)
    with pytest.raises(TypeError, match=r"Invalid data type for LocalParam"):
        LocalParam("8")
    with pytest.raises(TypeError, match=r"Invalid data type for LocalParam"):
        LocalParam(Signal(8))


def test_LocalParam_assemble():
    class Top(RawModule):
        @build
        def params(s):
            s.WIDTH = LocalParam(8)
            s.STEP = LocalParam(Bits(s.WIDTH, 2))
            s.REG_WIDTH = s.WIDTH * 2
            s.DATA_WIDTH = s.WIDTH

    top = Top()
    tree = AssembleHDL()(top)

    # LocalParam
    assert isinstance(top.WIDTH, LocalParam)
    assert top.WIDTH.name == "WIDTH"
    assert top.WIDTH.param_name == "WIDTH"
    assert isinstance(top.WIDTH.param_value, int)
    assert top.WIDTH.param_value == 8
    assert not top.WIDTH.is_expr
    assert isinstance(top.STEP, LocalParam)
    assert top.STEP.name == "STEP"
    assert top.STEP.param_name == "STEP"
    assert isinstance(top.STEP.param_value, Bits)
    assert top.STEP.param_value.nbits == 8
    assert top.STEP.param_value == 2
    assert top.STEP.param_value.width_param is top.WIDTH
    assert not top.STEP.is_expr
    assert isinstance(top.REG_WIDTH, LocalParam)
    assert top.REG_WIDTH.name == "REG_WIDTH"
    assert top.REG_WIDTH.param_name == "REG_WIDTH"
    assert isinstance(top.REG_WIDTH.param_value, int)
    assert top.REG_WIDTH.param_value == 16
    assert top.REG_WIDTH.is_expr
    assert top.REG_WIDTH.op == ParamConst.Op.MUL
    assert top.REG_WIDTH.left is top.WIDTH
    assert isinstance(top.REG_WIDTH.right, int) and top.REG_WIDTH.right == 2
    assert isinstance(top.DATA_WIDTH, LocalParam)
    assert top.DATA_WIDTH.name == "DATA_WIDTH"
    assert top.DATA_WIDTH.param_name == "DATA_WIDTH"
    assert isinstance(top.DATA_WIDTH.param_value, int)
    assert top.DATA_WIDTH.param_value == 8
    assert top.DATA_WIDTH.is_expr
    assert top.DATA_WIDTH.op == ParamConst.Op.ASSIGN
    assert top.DATA_WIDTH.left is top.WIDTH
    assert top.DATA_WIDTH.right is None

    # Nodes
    assert len(tree.elements) == 4
    assert tree.elements[0].obj is top.WIDTH
    assert tree.elements[0].name == "WIDTH"
    assert tree.elements[1].obj is top.STEP
    assert tree.elements[1].name == "STEP"
    assert tree.elements[2].obj is top.REG_WIDTH
    assert tree.elements[2].name == "REG_WIDTH"
    assert tree.elements[3].obj is top.DATA_WIDTH
    assert tree.elements[3].name == "DATA_WIDTH"
