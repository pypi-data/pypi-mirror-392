# Tests for HDLBits examples, procedures
#

import pytest

import comopy.testcases.ex_HDLBits_procedures as ex
from comopy.config import IRConfig, comopy_context
from comopy.testcases.checks import check_verilog

COMOPY_PROJECT_PATH = "."


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


def _translate(ModuleClass):
    check_verilog(ModuleClass, "ex_proc", COMOPY_PROJECT_PATH)


def test_procedures_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.Alwaysblock1)
    _translate(ex.Alwaysblock2)
    _translate(ex.Alwaysblock2_autoclk)
    _translate(ex.Always_if)
    _translate(ex.Always_if2)
    _translate(ex.Always_case)
    _translate(ex.Always_case2)
    _translate(ex.Always_casez)
    _translate(ex.Always_nolatches)
