# Tests for HDLBits examples, modules hierarchy
#

import pytest

import comopy.testcases.ex_HDLBits_modules as ex
from comopy.config import IRConfig, comopy_context
from comopy.testcases.checks import check_verilog

COMOPY_PROJECT_PATH = "."


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


def _translate(ModuleClass):
    check_verilog(ModuleClass, "ex_mod", COMOPY_PROJECT_PATH)


def test_modules_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.ModuleInst)
    # _translate(ex_mod.ModuleInst_local)  # local variable
    _translate(ex.Module_pos)
    _translate(ex.Module_name)
    _translate(ex.Module_shift)
    _translate(ex.Module_shift_autowire)
    _translate(ex.Module_shift8)
    _translate(ex.Module_add)
    _translate(ex.Module_fadd1)
    _translate(ex.Module_cseladd)
    _translate(ex.Module_addsub)
