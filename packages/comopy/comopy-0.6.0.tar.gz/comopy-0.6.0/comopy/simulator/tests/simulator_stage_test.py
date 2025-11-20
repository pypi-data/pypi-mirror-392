# Tests for SimulatorStage
#

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage, IRStage
from comopy.simulator.base_simulator import BaseSimulator
from comopy.simulator.simulator_stage import SimulatorStage


def test_SimulatorStage():
    top = ex.Wire1()
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    assert top.simulator is None
    assert not top.simulating
    tree_sim = SimulatorStage()(tree_ir)
    assert tree_sim is tree_ir
    sim = top.simulator
    assert isinstance(sim, BaseSimulator)

    sim.start()
    assert top.simulating
    top.in_ /= 1
    sim.evaluate()
    assert top.out == 1
    sim.stop()
    assert not top.simulating

    with pytest.raises(RuntimeError, match=r"simulation-time API"):
        top.out == 1


def test_SimulatorStage_error():
    s = SimulatorStage()
    with pytest.raises(TypeError, match="input must be an HDL.CircuitNode"):
        s(1)

    tree = HDLStage()(ex.Wire1())
    tree_ir = IRStage()(tree)
    with pytest.raises(ValueError, match="input must be the root"):
        s(tree_ir.elements[0])

    tree = HDLStage()(ex.Wire4())
    with pytest.raises(ValueError, match="has not been .* IR stage"):
        s(tree)
