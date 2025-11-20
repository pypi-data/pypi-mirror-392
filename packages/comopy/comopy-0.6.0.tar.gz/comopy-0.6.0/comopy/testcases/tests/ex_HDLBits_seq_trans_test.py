# Tests for HDLBits examples, sequential logic
#

import pytest

import comopy.testcases.ex_HDLBits_seq as ex
from comopy.config import IRConfig, comopy_context
from comopy.testcases.checks import check_verilog

COMOPY_PROJECT_PATH = "."


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


def _translate(ModuleClass):
    check_verilog(ModuleClass, "ex_seq", COMOPY_PROJECT_PATH)


def test_seq_raw_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.Dff_raw)
    _translate(ex.Dff8_raw)
    _translate(ex.Dff8r_raw)
    _translate(ex.Dff8p_raw)
    _translate(ex.Dff8ar_raw)
    _translate(ex.Dff16e_raw)
    _translate(ex.MuxDff_raw)


def test_seq_clk_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.Dff)
    _translate(ex.Dff8)
    _translate(ex.Dff8r)
    _translate(ex.Dff8ar)
    _translate(ex.Dff16e)
    _translate(ex.MuxDff)
