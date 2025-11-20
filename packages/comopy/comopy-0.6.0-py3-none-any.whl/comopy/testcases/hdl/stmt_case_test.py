# Tests for HDL statement: Case
#

import pytest

from comopy import *
from comopy import (  # for type checking
    BaseTestCase,
    Input,
    IOStruct,
    Output,
    RawModule,
    build,
    comb,
)


# Enable all debugging configurations
@pytest.fixture(scope="module", autouse=True)
def with_comopy_context():
    with comopy_context(ir_config=IRConfig.debug()):
        yield


class TestCaseConst(BaseTestCase):
    class CaseConst(RawModule):
        @build
        def ports(s):
            s.in_ = Input(4)
            s.sel = Input(2)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(4)
        sel = Input(2)
        out = Output()

    TV_all_cases = [
        IO(),
        (0b1101, 0b00, 1),
        (0b1101, 0b01, 0),
        (0b1101, 0b10, 1),
        (0b1101, 0b11, 1),
    ]

    TV_default = [
        IO(),
        (0b0101, 0b00, 1),
        (0b0101, 0b01, 0),
        (0b0101, 0b10, 1),
        (0b0101, 0b11, 1),
    ]

    class VecToInt(CaseConst):
        @comb
        def update(s):
            match s.sel:
                case 0:
                    s.out /= s.in_[0]
                case 1:
                    s.out /= s.in_[1]
                case 2:
                    s.out /= s.in_[2]
                case 3:
                    s.out /= s.in_[3]

    SV_vec_to_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (sel)\n"
        "      2'b00:\n"
        "        __out_bits = in_[0];\n"
        "      2'b01:\n"
        "        __out_bits = in_[1];\n"
        "      2'b10:\n"
        "        __out_bits = in_[2];\n"
        "      2'b11:\n"
        "        __out_bits = in_[3];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_vec_to_int(self):
        self.simulate(self.VecToInt(), self.TV_all_cases)
        self.translate(self.VecToInt(), self.SV_vec_to_int)

    class VecToIntDefault(CaseConst):
        @comb
        def update(s):
            match s.sel:
                case 0:
                    s.out /= s.in_[0]
                case 1:
                    s.out /= s.in_[1]
                case _:
                    s.out /= s.in_[2]

    SV_vec_to_int_default = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (sel)\n"
        "      2'b00:\n"
        "        __out_bits = in_[0];\n"
        "      2'b01:\n"
        "        __out_bits = in_[1];\n"
        "      default:\n"
        "        __out_bits = in_[2];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_vec_to_int_default(self):
        self.simulate(self.VecToIntDefault(), self.TV_default)
        self.translate(self.VecToIntDefault(), self.SV_vec_to_int_default)

    class EmptyDefault(CaseConst):
        @comb
        def update(s):
            s.out /= s.in_[2]
            match s.sel:
                case 0:
                    s.out /= s.in_[0]
                case 1:
                    s.out /= s.in_[1]
                case _:
                    pass  # empty default

    SV_empty_default = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out_bits = in_[2];\n"
        "    unique case (sel)\n"
        "      2'b00:\n"
        "        __out_bits = in_[0];\n"
        "      2'b01:\n"
        "        __out_bits = in_[1];\n"
        "      default: begin\n"
        "        // Empty default for unique case completeness\n"
        "      end\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_empty_default(self):
        self.simulate(self.EmptyDefault(), self.TV_default)
        self.translate(self.EmptyDefault(), self.SV_empty_default)

    class ExprToIntDefault(CaseConst):
        @comb
        def update(s):
            match 3 - s.sel:
                case 0:
                    s.out /= s.in_[3]
                case 1:
                    s.out /= s.in_[2]
                case 2:
                    s.out /= s.in_[1]
                case _:
                    s.out /= s.in_[0]

    SV_expr_to_int_default = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (2'h3 - sel)\n"
        "      2'b00:\n"
        "        __out_bits = in_[3];\n"
        "      2'b01:\n"
        "        __out_bits = in_[2];\n"
        "      2'b10:\n"
        "        __out_bits = in_[1];\n"
        "      default:\n"
        "        __out_bits = in_[0];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_expr_to_int_default(self):
        self.simulate(self.ExprToIntDefault(), self.TV_all_cases)
        self.translate(self.ExprToIntDefault(), self.SV_expr_to_int_default)

    class IfExprToInt(CaseConst):
        @comb
        def update(s):
            match 3 - s.sel if s.in_[3] else s.sel:
                case 0:
                    s.out /= s.in_[3]
                case 1:
                    s.out /= s.in_[2]
                case 2:
                    s.out /= s.in_[1]
                case 3:
                    s.out /= s.in_[0]

    TV_if_expr_to_int = [
        IO(),
        (0b1101, 0b00, 1),
        (0b1101, 0b01, 0),
        (0b1101, 0b10, 1),
        (0b1101, 0b11, 1),
        (0b0101, 0b00, 0),
        (0b0101, 0b01, 1),
        (0b0101, 0b10, 0),
        (0b0101, 0b11, 1),
    ]
    SV_if_expr_to_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (in_[3] ? 2'h3 - sel : sel)\n"
        "      2'b00:\n"
        "        __out_bits = in_[3];\n"
        "      2'b01:\n"
        "        __out_bits = in_[2];\n"
        "      2'b10:\n"
        "        __out_bits = in_[1];\n"
        "      2'b11:\n"
        "        __out_bits = in_[0];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_if_expr_to_int_default(self):
        self.simulate(self.IfExprToInt(), self.TV_if_expr_to_int)
        self.translate(self.IfExprToInt(), self.SV_if_expr_to_int)

    class SliceToInt(CaseConst):
        @comb
        def update(s):
            match s.sel[0, 2]:
                case 0:
                    s.out /= s.in_[0]
                case 1:
                    s.out /= s.in_[1]
                case 2:
                    s.out /= s.in_[2]
                case 3:
                    s.out /= s.in_[3]

    SV_slice_to_int = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (sel[32'h0 +: 2])\n"
        "      2'b00:\n"
        "        __out_bits = in_[0];\n"
        "      2'b01:\n"
        "        __out_bits = in_[1];\n"
        "      2'b10:\n"
        "        __out_bits = in_[2];\n"
        "      2'b11:\n"
        "        __out_bits = in_[3];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_slice_to_int(self):
        self.simulate(self.SliceToInt(), self.TV_all_cases)
        self.translate(self.SliceToInt(), self.SV_slice_to_int)

    class CatToIntDefault(CaseConst):
        @comb
        def update(s):
            match cat(s.sel[1:], s.sel[:1]):
                case 0:
                    s.out /= s.in_[0]
                case 1:
                    s.out /= s.in_[1]
                case 2:
                    s.out /= s.in_[2]
                case _:
                    s.out /= s.in_[3]

    SV_cat_to_int_default = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case ({sel[1], sel[0]})\n"
        "      2'b00:\n"
        "        __out_bits = in_[0];\n"
        "      2'b01:\n"
        "        __out_bits = in_[1];\n"
        "      2'b10:\n"
        "        __out_bits = in_[2];\n"
        "      default:\n"
        "        __out_bits = in_[3];\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_cat_to_int_default(self):
        self.simulate(self.CatToIntDefault(), self.TV_all_cases)
        self.translate(self.CatToIntDefault(), self.SV_cat_to_int_default)


class TestCaseWildcard(BaseTestCase):
    class CaseWildcard(RawModule):
        @build
        def ports(s):
            s.in_ = Input(8)
            s.sel = Input(8)
            s.out = Output()

    class IO(IOStruct):
        in_ = Input(8)
        sel = Input(8)
        out = Output()

    class VecToZ(CaseWildcard):
        @comb
        def update(s):
            match s.sel:
                case "1???_????":
                    s.out /= s.in_[7]
                case "01??_????":
                    s.out /= s.in_[6]
                case "001?_????":
                    s.out /= s.in_[5]
                case "0001_????":
                    s.out /= s.in_[4]
                case "0000_0111":
                    s.out /= 0
                case "0000_0???":
                    s.out /= s.in_[s.sel[:3]]
                case _:
                    s.out /= 0

    TV_vec_to_z = [
        IO(),
        (0b10100101, 0b10011001, 1),
        (0b10100101, 0b01000100, 0),
        (0b10100101, 0b00111000, 1),
        (0b10100101, 0b00010010, 0),
        (0b10100101, 0b00001010, 0),
        (0b10100101, 7, 0),
        (0b10100101, 5, 1),
        (0b10100101, 4, 0),
        (0b10100101, 2, 1),
        (0b10100101, 0, 1),
    ]
    SV_vec_to_z = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    casez (sel)\n"
        "      8'b1zzzzzzz:\n"
        "        __out_bits = in_[7];\n"
        "      8'b01zzzzzz:\n"
        "        __out_bits = in_[6];\n"
        "      8'b001zzzzz:\n"
        "        __out_bits = in_[5];\n"
        "      8'b0001zzzz:\n"
        "        __out_bits = in_[4];\n"
        "      8'b00000111:\n"
        "        __out_bits = 1'h0;\n"
        "      8'b00000zzz:\n"
        "        __out_bits = in_[sel[2:0] +: 1];\n"
        "      default:\n"
        "        __out_bits = 1'h0;\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_vec_to_z(self):
        self.simulate(self.VecToZ(), self.TV_vec_to_z)
        self.translate(self.VecToZ(), self.SV_vec_to_z)

    class VecToIntZ(CaseWildcard):
        @comb
        def update(s):
            match s.sel:
                case "1???_????":
                    s.out /= s.in_[7]
                case "01??_????":
                    s.out /= s.in_[6]
                case "001?_????":
                    s.out /= s.in_[5]
                case "0001_????":
                    s.out /= s.in_[4]
                case 7:
                    s.out /= 0
                case "0000_0???":
                    s.out /= s.in_[s.sel[:3]]
                case _:
                    s.out /= 0

    def test_vec_to_int_z(self):
        self.simulate(self.VecToIntZ(), self.TV_vec_to_z)
        self.translate(self.VecToIntZ(), self.SV_vec_to_z)

    class ExprToZ(CaseWildcard):
        @comb
        def update(s):
            match s.sel & b8(0xFF):
                case "1???_????":
                    s.out /= s.in_[7]
                case "01??_????":
                    s.out /= s.in_[6]
                case "001?_????":
                    s.out /= s.in_[5]
                case "0001_????":
                    s.out /= s.in_[4]
                case "0000_0111":
                    s.out /= 0
                case "0000_0???":
                    s.out /= s.in_[s.sel[:3]]
                case _:
                    s.out /= 0

    SV_expr_to_z = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    casez (sel & 8'hFF)\n"
        "      8'b1zzzzzzz:\n"
        "        __out_bits = in_[7];\n"
        "      8'b01zzzzzz:\n"
        "        __out_bits = in_[6];\n"
        "      8'b001zzzzz:\n"
        "        __out_bits = in_[5];\n"
        "      8'b0001zzzz:\n"
        "        __out_bits = in_[4];\n"
        "      8'b00000111:\n"
        "        __out_bits = 1'h0;\n"
        "      8'b00000zzz:\n"
        "        __out_bits = in_[sel[2:0] +: 1];\n"
        "      default:\n"
        "        __out_bits = 1'h0;\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_expr_to_z(self):
        self.simulate(self.ExprToZ(), self.TV_vec_to_z)
        self.translate(self.ExprToZ(), self.SV_expr_to_z)

    class SliceToIntZ(CaseWildcard):
        @comb
        def update(s):
            match s.sel[0, 8]:
                case "1???_????":
                    s.out /= s.in_[7]
                case "01??_????":
                    s.out /= s.in_[6]
                case "001?_????":
                    s.out /= s.in_[5]
                case "0001_????":
                    s.out /= s.in_[4]
                case 7:
                    s.out /= 0
                case "0000_0???":
                    s.out /= s.in_[s.sel[:3]]
                case _:
                    s.out /= 0

    SV_slice_to_int_z = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    casez (sel[32'h0 +: 8])\n"
        "      8'b1zzzzzzz:\n"
        "        __out_bits = in_[7];\n"
        "      8'b01zzzzzz:\n"
        "        __out_bits = in_[6];\n"
        "      8'b001zzzzz:\n"
        "        __out_bits = in_[5];\n"
        "      8'b0001zzzz:\n"
        "        __out_bits = in_[4];\n"
        "      8'b00000111:\n"
        "        __out_bits = 1'h0;\n"
        "      8'b00000zzz:\n"
        "        __out_bits = in_[sel[2:0] +: 1];\n"
        "      default:\n"
        "        __out_bits = 1'h0;\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_slice_to_int_z(self):
        self.simulate(self.SliceToIntZ(), self.TV_vec_to_z)
        self.translate(self.SliceToIntZ(), self.SV_slice_to_int_z)

    class CatToIntZ(CaseWildcard):
        @comb
        def update(s):
            match cat(s.sel[4:], s.sel[:4]):
                case "1???_????":
                    s.out /= s.in_[7]
                case "01??_????":
                    s.out /= s.in_[6]
                case "001?_????":
                    s.out /= s.in_[5]
                case "0001_????":
                    s.out /= s.in_[4]
                case 7:
                    s.out /= 0
                case "0000_0???":
                    s.out /= s.in_[s.sel[:3]]
                case _:
                    s.out /= 0

    SV_cat_to_int_z = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    casez ({sel[7:4], sel[3:0]})\n"
        "      8'b1zzzzzzz:\n"
        "        __out_bits = in_[7];\n"
        "      8'b01zzzzzz:\n"
        "        __out_bits = in_[6];\n"
        "      8'b001zzzzz:\n"
        "        __out_bits = in_[5];\n"
        "      8'b0001zzzz:\n"
        "        __out_bits = in_[4];\n"
        "      8'b00000111:\n"
        "        __out_bits = 1'h0;\n"
        "      8'b00000zzz:\n"
        "        __out_bits = in_[sel[2:0] +: 1];\n"
        "      default:\n"
        "        __out_bits = 1'h0;\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_cat_to_int_z(self):
        self.simulate(self.CatToIntZ(), self.TV_vec_to_z)
        self.translate(self.CatToIntZ(), self.SV_cat_to_int_z)


class TestCaseBodies(BaseTestCase):
    class CaseConst(RawModule):
        @build
        def ports(s):
            s.in_ = Input(4)
            s.sel = Input(2)
            s.out1 = Output()
            s.out2 = Output()

    class IO(IOStruct):
        in_ = Input(4)
        sel = Input(2)
        out1 = Output()
        out2 = Output()

    class CaseBodies(CaseConst):
        @comb
        def update(s):
            match s.sel:
                case 0:
                    s.out1 /= s.in_[0]
                    s.out2 /= s.in_[1]
                case 1:
                    s.out1 /= s.in_[2]
                    s.out2 /= s.in_[3]
                case _:
                    s.out1 /= 0
                    s.out2 /= 0

    TV_case_bodies = [
        IO(),
        (0b1101, 0b00, 1, 0),
        (0b1101, 0b01, 1, 1),
        (0b1101, 0b10, 0, 0),
        (0b1101, 0b11, 0, 0),
    ]
    SV_case_bodies = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    unique case (sel)\n"
        "      2'b00: begin\n"
        "        __out1_bits = in_[0];\n"
        "        __out2_bits = in_[1];\n"
        "      end\n"
        "      2'b01: begin\n"
        "        __out1_bits = in_[2];\n"
        "        __out2_bits = in_[3];\n"
        "      end\n"
        "      default: begin\n"
        "        __out1_bits = 1'h0;\n"
        "        __out2_bits = 1'h0;\n"
        "      end\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_case_block(self):
        self.simulate(self.CaseBodies(), self.TV_case_bodies)
        self.translate(self.CaseBodies(), self.SV_case_bodies)

    class CaseIf(CaseConst):
        @comb
        def update(s):
            s.out1 /= 0
            s.out2 /= 0
            match s.sel:
                case 0:
                    if s.in_[3]:
                        s.out1 /= s.in_[0]
                        s.out2 /= s.in_[1]
                case 1:
                    if s.in_[0]:
                        s.out1 /= s.in_[2]
                    else:
                        s.out2 /= s.in_[3]
                case _:
                    pass

    TV_case_if = [
        IO(),
        (0b1101, 0b00, 1, 0),
        (0b1101, 0b01, 1, 0),
        (0b1101, 0b10, 0, 0),
        (0b1101, 0b11, 0, 0),
    ]
    SV_case_if = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out2_bits = 1'h0;\n"
        "    unique case (sel)\n"
        "      2'b00: begin\n"
        "        if (in_[3]) begin\n"
        "          __out1_bits = in_[0];\n"
        "          __out2_bits = in_[1];\n"
        "        end\n"
        "      end\n"
        "      2'b01: begin\n"
        "        if (in_[0])\n"
        "          __out1_bits = in_[2];\n"
        "        else\n"
        "          __out2_bits = in_[3];\n"
        "      end\n"
        "      default: begin\n"
        "        // Empty default for unique case completeness\n"
        "      end\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_case_if(self):
        self.simulate(self.CaseIf(), self.TV_case_if)
        self.translate(self.CaseIf(), self.SV_case_if)

    class CaseNested(CaseConst):
        @comb
        def update(s):
            s.out1 /= 0
            s.out2 /= 0
            match s.sel:
                case 0:
                    match s.in_[2:]:
                        case 0:
                            s.out1 /= s.in_[0]
                            s.out2 /= s.in_[1]
                        case _:
                            s.out1 /= s.in_[2]
                            s.out2 /= s.in_[3]
                case _:
                    match s.in_[:2]:
                        case 0:
                            s.out1 /= s.in_[2]
                        case 2:
                            s.out2 /= s.in_[3]
                        case _:
                            s.out1 /= 1
                            s.out2 /= 1

    TV_case_nested = [
        IO(),
        (0b1101, 0b00, 1, 1),
        (0b1101, 0b01, 1, 1),
        (0b1101, 0b10, 1, 1),
        (0b1101, 0b11, 1, 1),
    ]
    SV_case_nested = (
        "  // @comb update():\n"
        "  always_comb begin\n"
        "    __out1_bits = 1'h0;\n"
        "    __out2_bits = 1'h0;\n"
        "    unique case (sel)\n"
        "      2'b00: begin\n"
        "        unique case (in_[3:2])\n"
        "          2'b00: begin\n"
        "            __out1_bits = in_[0];\n"
        "            __out2_bits = in_[1];\n"
        "          end\n"
        "          default: begin\n"
        "            __out1_bits = in_[2];\n"
        "            __out2_bits = in_[3];\n"
        "          end\n"
        "        endcase\n"
        "      end\n"
        "      default: begin\n"
        "        unique case (in_[1:0])\n"
        "          2'b00:\n"
        "            __out1_bits = in_[2];\n"
        "          2'b10:\n"
        "            __out2_bits = in_[3];\n"
        "          default: begin\n"
        "            __out1_bits = 1'h1;\n"
        "            __out2_bits = 1'h1;\n"
        "          end\n"
        "        endcase\n"
        "      end\n"
        "    endcase\n"
        "  end // always_comb"
    )

    def test_case_nested(self):
        self.simulate(self.CaseNested(), self.TV_case_nested)
        self.translate(self.CaseNested(), self.SV_case_nested)
