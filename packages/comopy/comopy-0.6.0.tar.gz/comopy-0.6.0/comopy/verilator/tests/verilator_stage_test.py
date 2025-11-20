# Tests for VerilatorStage
#

from pathlib import Path

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage, IRStage, JobPipeline, TranslatorStage
from comopy.config import TranslatorConfig, comopy_context
from comopy.verilator.verilator_stage import VerilatorStage
from comopy.verilator.vsimulator import VSimulator

_tests_out = "comopy/tests_out"


def test_VerilatorStage(project_path):
    pipeline = JobPipeline(
        HDLStage(), IRStage(), TranslatorStage(), VerilatorStage()
    )
    top = ex.Andgate(name="top")

    path = Path(f"{project_path}/{_tests_out}/build").resolve()
    trans_config = TranslatorConfig(dest_dir=str(path))
    with comopy_context(trans_config=trans_config):
        pipeline(top)

    vsim = top.vsimulator
    assert isinstance(vsim, VSimulator)
    assert vsim.module is top
    vsim.start()
    vsim_top = vsim.vsim_top
    vsim_top.a = 1
    vsim_top.b = 0
    vsim.evaluate()
    assert vsim_top.out == 0
    vsim_top.a = 1
    vsim_top.b = 1
    vsim.evaluate()
    assert vsim_top.out == 1
    vsim.stop()

    with pytest.raises(RuntimeError, match="Cannot access 'vsim_top' without"):
        vsim.vsim_top


def test_VerilatorStage_error():
    s = VerilatorStage()
    with pytest.raises(TypeError, match="input must be an HDL.CircuitNode"):
        s(1)

    pipeline = JobPipeline(HDLStage(), IRStage(), TranslatorStage())
    tree = pipeline(ex.Wire1())
    with pytest.raises(ValueError, match="input must be the root"):
        s(tree.elements[0])

    pipeline = JobPipeline(HDLStage(), IRStage())
    tree = pipeline(ex.Wire4())
    with pytest.raises(ValueError, match="has not been .* translator stage"):
        s(tree)
