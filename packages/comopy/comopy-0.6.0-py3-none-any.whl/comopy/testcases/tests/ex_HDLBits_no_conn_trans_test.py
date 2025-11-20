# Tests for HDLBits examples, basics and vectors (without @=)
#

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy.config import IRConfig, comopy_context
from comopy.testcases.checks import check_verilog

COMOPY_PROJECT_PATH = "."


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


def _translate(ModuleClass):
    check_verilog(ModuleClass, "ex_no_conn", COMOPY_PROJECT_PATH)


def test_comb_basics_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.Wire1)
    _translate(ex.Wire4)
    _translate(ex.Notgate)
    _translate(ex.Andgate)
    _translate(ex.Norgate)
    _translate(ex.Xnorgate)
    _translate(ex.WireDecl)


def test_comb_vectors_verilog(project_path):
    global COMOPY_PROJECT_PATH
    COMOPY_PROJECT_PATH = project_path
    _translate(ex.Vector0)
    _translate(ex.Vector1)
    _translate(ex.Vector2)
    _translate(ex.Vectorgates)
    _translate(ex.Gates4)
    _translate(ex.Vector3)
    _translate(ex.Vectorrev1)
    _translate(ex.Vectorrev1_cat_lhs)
    _translate(ex.Vector4)
    _translate(ex.Vector5)
