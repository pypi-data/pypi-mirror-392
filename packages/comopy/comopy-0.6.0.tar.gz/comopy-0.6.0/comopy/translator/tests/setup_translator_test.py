# Tests for SetupTranslator
#

import pytest

import comopy.testcases.ex_HDLBits_no_conn as ex
from comopy import HDLStage, IRStage
from comopy.config import TranslatorConfig, comopy_context
from comopy.translator.setup_translator import SetupTranslator
from comopy.translator.verilog_translator import VerilogTranslator


def test_SetupTranslator_call():
    sv_top = (
        "module Wire1(\n"
        "  input  wire in_,\n"
        "  output wire out\n"
        ");\n"
        "\n"
        "  // Variables for output ports\n"
        "  logic __out_bits;\n"
        "\n"
        "  // @comb update():\n"
        "  always_comb\n"
        "    __out_bits = in_;\n"
        "\n"
        "  assign out = __out_bits;\n"
        "endmodule"
    )

    top = ex.Wire1(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)
    tree_trans = SetupTranslator()(tree_ir)
    assert tree_trans is tree_ir
    trans = top.translator
    assert isinstance(trans, VerilogTranslator)
    assert trans.target_language == "SystemVerilog"
    assert trans.file_extension == ".sv"
    assert trans.dest_path.name == "Wire1.sv"

    sv = trans.emit()
    assert sv == sv_top

    with pytest.raises(RuntimeError, match=r"Translator .* 'top' has already"):
        SetupTranslator()(tree_ir)


def test_SetupTranslator_error(tmp_path):
    """Test SetupTranslator validation of dest_dir configuration."""
    top = ex.Wire1(name="top")
    tree = HDLStage()(top)
    tree_ir = IRStage()(tree)

    # Relative path
    with comopy_context(trans_config=TranslatorConfig(dest_dir="a/b")):
        with pytest.raises(ValueError, match=r"'dest_dir' .* an absolute"):
            SetupTranslator()(tree_ir)

    # Path exists but is a file
    path = tmp_path / "not_a_dir.txt"
    path.write_text("test")
    with comopy_context(trans_config=TranslatorConfig(dest_dir=str(path))):
        with pytest.raises(ValueError, match=r"'dest_dir' exists.* not a dir"):
            SetupTranslator()(tree_ir)
